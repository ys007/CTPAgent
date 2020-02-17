#coding=utf-8
"""
重点是解析xml得到自己想要的结果
将最终解析得到的数据存储为csv
"""

import nmap
import json
import re
import os
import time
from xml.dom.minidom import Document  #将文件存储为xml格式
from xml.dom.minidom import parse
from xml.etree import ElementTree as et
import csv
import xlsxwriter
from datetime import date, datetime

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

#read the nmap.exe path
def readpath():
    f = open(r"path.txt","r")
    path = f.readline()
    #redisIP = line.split(":")
    return path


#read ip
def readip():
    f = open(r"IP.txt","r")
    ip = f.readline()
    return ip

#read port
def readport():
    f = open(r"port.txt","r")
    port = f.readline()
    return port

#read arguments
def readarguments():
    f = open(r"arguments.txt","r")
    arguments = f.readline()
    return arguments


#save extracted data.json
def savedata(id,timest,time_format,result,number):
    one = {"id": 1, "timest": "123123113", "datetime": "2010-01-01 19:12:12", "result": "success"}
    one['id']=id
    one['timest']=timest.encode("utf-8")
    one['datetime']= time_format
    one['result']=result
    mess1 = {'这里是定制的结果': '1'}
    mess1['这里是定制的结果'] = number
    two = {"detail": mess1}
    #data = dict(one)
    # one.keys().encode("utf-8")
    # one.values.encode("utf-8")
    jsonData = json.dumps(one,ensure_ascii=False,default=str)

    fileObject = open('data.json', 'w')
    fileObject.write(jsonData)
    fileObject.close()

#save raw data.xml
def saveraw(raw):
    # xmlraw = raw
    # dom = parseString(xmlraw)
    # xmlraw1=dom.toprettyxml(indent='')
    f = open('rawdata.xml', 'w',encoding='utf-8')
    xmlraw1=re.sub('[\r\n\f]{2,}','\n',raw)#用正则表达式去空行
    f.write(xmlraw1)
    f.close()


def analysisxml(raw):
    datas_list=[]
    for host in raw.iter('host'):
        if host.find('status').get('state')=='down':
            continue
        address=host.find('address').get('addr',None)
        print("ip是：",address)
        if not address:
            continue
        ports=[]
        for port in host.iter('port'):
            state=port.find('state').get('state','')
            portid=port.get('portid',None)
            serv=port.find('service').get('name','')
            ports.append([portid,serv,state])
        datas_list.append({address:ports})
    return datas_list



#save port information
# def Write_csv(f_csv,datas): #写入csv文件中
#     # file_csv = "test.csv"  # csv文件名
#     headers = ["id","ip", "port", "state", "service"]
#     with open(f_csv, "w") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(headers)#写入标题
#         index=0
#         for index,item in enumerate(datas):
#             for ip,ports in item.items():
#                 port_num=len(ports)
#                 if not ports:
#                     continue
#                 index=index+1
#                 # for i,data in enumerate(ports):

def reportEXCEL(filename,datalst,title=TITLE,style=DEFAULT_STYLE,**kwargs):
    if not datalst:
        return ''
    if  os.path.exists(filename):
        print (u"%s 文件已经存在" % filename)
        path,name=os.path.split(filename)
        filename=os.path.splitext(name)[0]
        filename=filename+str(time.strftime("%Y%m%d%H%M%S",time.localtime()))+'.xlsx'
        filename=os.path.join(path,filename)
        print ('data will save as new file named :%s ' % filename)

    book=xlsxwriter.Workbook(filename)
    title_style= style if not kwargs.get('title',None) else kwargs.get('title')

    row_hight=[20,16] if not kwargs.get('row_set',None) else kwargs.get('row_set')    #标题题和常规的高度
    # col_width=[8,22] if not kwargs.get('col_set',None) else kwargs.get('col_set') #序号，其他宽度
    sheet_name= 'sheet' if not kwargs.get('sheet_name',None) else kwargs.get('sheet_name')
    sheet=book.add_worksheet(sheet_name)

    row_hight=row_hight+(2000-len(row_hight))*[row_hight[-1]]
    for row , h in enumerate(row_hight):
        sheet.set_row(row,h)
    col_width=map(lambda x:x[1],title)
    for col , w in enumerate(col_width):
        sheet.set_column(col,col,w)
    title_style = book.add_format(title_style)
    for index,t in enumerate(title):

        sheet.write(0,index,t[0],title_style)

    row=1
    col=0
    style=book.add_format(style)
    index2=0
    for index,item in enumerate(datalst):
        # print item
        for ip,ports in item.items():
            port_num=len(ports)
            if not ports:
                continue
            index2=index2+1
            for  i,data in enumerate(ports):


                sheet.write(row,2,data[0],style)
                sheet.write(row,3,data[1],style)
                sheet.write(row,4,data[2],style)
                row = row + 1
            if row-port_num+1 != row:
                sheet.merge_range('B'+str(row-port_num+1)+':B'+str(row),ip,style)
                sheet.merge_range('A'+str(row-port_num+1)+':A'+str(row),index2,style)
            else:
                # print index2
                sheet.write(row-1,0,index2,style)
                sheet.write(row-1,1,ip,style)
    print('Reprot result of xml parser to file: %s' % filename)
    book.close()


if __name__ == '__main__':
    path = readpath()
    ip = readip()
    port = readport()
    arguments = readarguments()
    nm = nmap.PortScanner(nmap_search_path=('nmap', path))
    results = nm.scan(ip, port, arguments)
    raw = nm.get_nmap_last_output()
    saveraw(raw)#存储原先的数据为xml
    a = nm.command_line()
    # print(ip,port,arguments)
    # print(raw)
    # print(a)
    # print(results)
    # 以下为协议的解析过程，解析到自己需要的数据,是通过得到的结果直接解析的

    # 通过判断scaninfo来判定这条语句是否成功
    info = results['nmap']['scaninfo']
    keys = list(info.keys())
    if keys[0] == 'error':
        result = 'fail'
    else:
        result = 'success'

    # print(info)
    # print(keys[0])
    # print(results)

    id = 2

    GMT_FORMAT = "%a %b %d %H:%M:%S %Y"
    timest = results['nmap']['scanstats']['elapsed']
    datetime1 = results['nmap']['scanstats']['timestr']
    time_format1 = datetime.strptime(datetime1, GMT_FORMAT)
    print(time_format1)
    number = '6'
    savedata(id, timest, time_format1, result, number) #存储一些自己想要的结果

    # data222 = open("rawdata.xml").read() #验证data222和raw的数据是一样的
    # print("shuchu",data222)
    # root = parse("./rawdata.xml")
    # rootNode = root.documentElement
    # raw.documentElement
    root = et.fromstring(raw)
    print("root的根元素:",root.tag)
    #查看有哪些子元素

    # for child_of_root in root:
    #     print (child_of_root.tag, child_of_root.attrib)
    #
    # for child_of_root in root[3]:
    #     print(child_of_root.tag, child_of_root.attrib)

    # t1 = root.findall("host")

    data_list=analysisxml(root)
    file_csv="port.xls"
    print("data_list：",data_list)
    # Write_csv(file_csv,data_list)
    reportEXCEL(file_csv,data_list)




