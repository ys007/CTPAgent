#coding=utf-8
"""
重点是解析xml得到自己想要的结果
将最终解析得到的数据存储为csv

应该是形成两个json格式一个用于存放在redis中：{"type":"security","subType":"nmap","status":"running","owner":"测试id"}
key是AGENTIP:PORT
还有一个json格式是用来返回服务端响应的返回字段至少有status和msg
"""

import nmap
import re
import os
import time
from xml.etree import ElementTree as et
import xlsxwriter
from datetime import date, datetime
from app.utils.util import sendStatusToRedis
from config import Config

TITLE=[
    (u'序号',8),
    ('IP',22),
    (u'端口',10),
    (u'服务',18),
    (u'开放状态',15),
]

DEFAULT_STYLE={
        'font_size': 12,  # 字体大小
        'bold': False,  # 是否粗体
        # 'bg_color': '#101010',  # 表格背景颜色
        'font_color': 'black',  # 字体颜色
        'align': 'left',  # 居中对齐
        'valign':'vcenter',
        'font_name':'Courier New',
        'top': 2,  # 上边框
        # 后面参数是线条宽度
        'left': 2,  # 左边框
        'right': 2,  # 右边框
        'bottom': 2  # 底边框
}

#save extracted data.json
def update_redis_abstract(id,timest,time_format,abs_status,abs_msg):
    one ={"agentid": '1', "timest": "", "datetime": "","status":"","msg":""}
    one['agentid']=id
    one['timest']=timest
    one['datetime']= str(time_format)
    one['status']=abs_status
    one['msg']=abs_msg

    # sendStatusToRedis(one)   #修改规则，不在这里向redis发送测试信息##################################################

# save raw data.xml
def saveraw(key_name, raw):
    # xmlraw = raw
    # dom = parseString(xmlraw)
    # xmlraw1=dom.toprettyxml(indent='')
    xml_name = '%s.xml' % key_name
    f = open(xml_name, 'w', encoding='utf-8')
    xmlraw1 = re.sub('[\r\n\f]{2,}', '\n', raw)  # 用正则表达式去空行
    f.write(xmlraw1)
    f.close()


def analysisxml(raw):
    datas_list = []
    datas_list_open = []
    for host in raw.iter('host'):
        if host.find('status').get('state') == 'down':
            continue
        address = host.find('address').get('addr', None)
        print("ip是：", address)
        if not address:
            continue
        ports = []
        ports_open = []
        ports_closed = []
        ports_filtered = []
        ports_unfilterd = []
        ports_Ofiltered = []
        ports_Cfiltered = []
        for port in host.iter('port'):
            state = port.find('state').get('state', '')
            portid = port.get('portid', None)
            serv = port.find('service').get('name', '')
            if state == 'open':
                # ports_open.append([portid,serv,state])
                ports_open.append(portid)
            if state == 'closed':
                ports_closed.append(portid)
            if state == 'Filtered':
                ports_filtered.append(portid)
            if state == 'unfilterd':
                ports_unfilterd.append(portid)
            if state == 'Open|filtered':
                ports_Ofiltered.append(portid)
            if state == 'Closed|filtered':
                ports_Cfiltered.append(portid)
            ports.append([portid, serv, state])
        datas_list.append({address: ports})
        datas_list_open.append({address: ports_open})
    return datas_list, ports_open, ports_closed, ports_filtered, ports_unfilterd, ports_Ofiltered, ports_Cfiltered


# save port information
def saveEXCEL(filename, datalst, title=TITLE, style=DEFAULT_STYLE, **kwargs):
    if not datalst:
        return ''
    if os.path.exists(filename):
        print(u"%s 文件已经存在" % filename)
        path, name = os.path.split(filename)
        filename = os.path.splitext(name)[0]
        filename = filename + str(time.strftime("%Y%m%d%H%M%S", time.localtime())) + '.xlsx'
        filename = os.path.join(path, filename)
        print('data will save as new file named :%s ' % filename)

    book = xlsxwriter.Workbook(filename)
    title_style = style if not kwargs.get('title', None) else kwargs.get('title')

    row_hight = [20, 16] if not kwargs.get('row_set', None) else kwargs.get('row_set')  # 标题题和常规的高度
    # col_width=[8,22] if not kwargs.get('col_set',None) else kwargs.get('col_set') #序号，其他宽度
    sheet_name = 'sheet' if not kwargs.get('sheet_name', None) else kwargs.get('sheet_name')
    sheet = book.add_worksheet(sheet_name)

    row_hight = row_hight + (2000 - len(row_hight)) * [row_hight[-1]]
    for row, h in enumerate(row_hight):
        sheet.set_row(row, h)
    col_width = map(lambda x: x[1], title)
    for col, w in enumerate(col_width):
        sheet.set_column(col, col, w)
    title_style = book.add_format(title_style)
    for index, t in enumerate(title):
        sheet.write(0, index, t[0], title_style)

    row = 1
    col = 0
    style = book.add_format(style)
    index2 = 0
    for index, item in enumerate(datalst):
        # print item
        for ip, ports in item.items():
            port_num = len(ports)
            if not ports:
                continue
            index2 = index2 + 1
            for i, data in enumerate(ports):
                sheet.write(row, 2, data[0], style)
                sheet.write(row, 3, data[1], style)
                sheet.write(row, 4, data[2], style)
                row = row + 1
            if row - port_num + 1 != row:
                sheet.merge_range('B' + str(row - port_num + 1) + ':B' + str(row), ip, style)
                sheet.merge_range('A' + str(row - port_num + 1) + ':A' + str(row), index2, style)
            else:
                # print index2
                sheet.write(row - 1, 0, index2, style)
                sheet.write(row - 1, 1, ip, style)
    print('Reprot result of xml parser to file: %s' % filename)
    book.close()

###############################################
#合并两个nmap扫描结果的xml字符串
#把sourceString中的<host   /host>部分内容拼接到targetString中，并输出最终拼接好的字符串，若targetString为“”，直接返回sourceString
###############################################
def merge(sourceString, targetString):
    #1、如果targetString为空，说明是第一次执行，不需要合并，直接把sourceString返回即可
    if targetString == "":
        return sourceString

    #2、得到sourceString中“<host”和"</host>"中间的内容
    hosts = sourceString[sourceString.find("<host") : sourceString.rfind("</host>") + len("</host>")]

    #3、把targetString以最后一个</host>为分界点，拆成两个字符串
    targetString1 = targetString[0 : targetString.rfind("</host>") + len("</host>")]
    targetString2 = targetString[targetString.rfind("</host>") + len("</host>"):]

    #4、把hosts的内容放到targetString1和targetString2中间
    return targetString1 + hosts + targetString2

def results(ip, port, arguments):
    # json_data={"status": "","msg":"","file":"","key":key_name}
    #nm = nmap.PortScanner(nmap_search_path=('nmap', r"C:\Program Files (x86)\Nmap\nmap.exe"))
    nm = nmap.PortScanner(nmap_search_path=('nmap', Config.NMAP_PATH))
    results = nm.scan(ip, port, arguments)
    raw = nm.get_nmap_last_output()
    # json_data["file"]=raw
    # saveraw(key_name,raw)  # 存储原先的数据为xml
    # a = nm.command_line()
    # print("raw是",raw)
    # print(a)
    # 以下为协议的解析过程，解析到自己需要的数据,是通过得到的结果直接解析的
    # 通过判断scaninfo来判定这条语句是否成功
    info = results['nmap']['scaninfo']
    # print("输出的info为",info)
    keys = list(info.keys())
    if keys[0] == 'error':
        json_status = '500'  # 代表nmap语句执行失败
        abs_status = '500'
        msg = info[keys[0]]
        msg = msg[0]
        json_msg = msg
        abs_msg = msg
        print("msg是", msg)
    else:
        json_status = '200'  # 代表nmap语句执行成功
        abs_status = '200'
        json_msg = '该用例执行成功'
        # 只有在执行成功的时候才会保存端口信息
        # data222 = open("rawdata.xml").read() #验证data222和raw的数据是一样的
        # root = parse("./rawdata.xml")
        # rootNode = root.documentElement
        # raw.documentElement
        root = et.fromstring(raw)
        # print("root的根元素:", root.tag)
        # 查看有哪些子元素
        # for child_of_root in root:
        #     print (child_of_root.tag, child_of_root.attrib)
        # t1 = root.findall("host")

        datas_list,ports_open,ports_closed,ports_filtered,ports_unfilterd,ports_Ofiltered,ports_Cfiltered = analysisxml(root)
        abs_msg="open:%d,closed:%d,filtered:%d,unfilterd:%d,Open|filtered:%d,Closed|filtered:%d"%(len(ports_open),len(ports_closed),len(ports_filtered),len(ports_unfilterd),len(ports_Ofiltered),len(ports_Cfiltered))
        print("abs_msg是", abs_msg)
        file_csv = "port.xls"
        print("data_list：", datas_list)
        saveEXCEL(file_csv, datas_list)
    id = '1'
    GMT_FORMAT = "%a %b %d %H:%M:%S %Y"
    timest = results['nmap']['scanstats']['elapsed']
    datetime1 = results['nmap']['scanstats']['timestr']
    time_format1 = datetime.strptime(datetime1, GMT_FORMAT)
    # print(time_format1)
    update_redis_abstract(id,timest, time_format1,abs_status,abs_msg)  # 存储一些概要信息   关于redis的部分暂时未写
    return  json_status,json_msg,raw,timest #返回值

if __name__ == '__main__':

    ip='127.0.0.1'
    port='80-84'
    arguments='-Pn -sS -A'
    key_name="1_data"  #这个key是对应的redis的概要信息
    re=results(ip,port,arguments)#传入参数key_name 不传入
    # print(re)






