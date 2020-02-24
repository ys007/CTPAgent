#coding=utf-8
"""
重点是解析xml得到自己想要的结果
将最终解析得到的数据存储为csv

应该是形成两个json格式一个用于存放在redis中：{"type":"security","subType":"nmap","status":"running","owner":"测试id"}
key是AGENTIP:PORT
还有一个json格式是用来返回服务端响应的返回字段至少有status和msg
"""

import nmap
import redis
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
def update_redis_abstract(key_name,id,timest,time_format):
    one ={"agentid": '1', "timest": "", "datetime": ""}
    one['agentid']=id
    one['timest']=timest
    one['datetime']= time_format
   # mess1 = {'这里是定制的结果': '1'}
    #mess1['这里是定制的结果'] = number
    # two = {"msg": msg}
    # data = dict(one,**two)
    jsonData = json.dumps(one,ensure_ascii=False,default=str)
    r = redis.StrictRedis(host="127.0.0.1", db=0, password='1', decode_responses=True)
    if r.exists(key_name):
        r.delete(key_name)
    r.set(key_name,jsonData)  # key值暂时先固定，如果有需要后边会进行改动

    # 不将结果存储到文件中，直接返回一个json格式的值
    # fileObject = open('data.json', 'w',encoding='utf-8')
    # fileObject.write(jsonData)
    # fileObject.close()

#save raw data.xml
def saveraw(key_name,raw):
    # xmlraw = raw
    # dom = parseString(xmlraw)
    # xmlraw1=dom.toprettyxml(indent='')
    xml_name='%s.xml'%key_name
    f = open(xml_name, 'w',encoding='utf-8')
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

def saveEXCEL(filename,datalst,title=TITLE,style=DEFAULT_STYLE,**kwargs):
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

# update redis
def update_redis_status(status,owner):  #redis 的状态信息 状态信息的key为ip：port
    r = redis.StrictRedis(host="127.0.0.1", db=0, password='1', decode_responses=True)
    jsonredis={"type": "security", "subType": "nmap", "status": status, "owner": owner}
    key_status="127.0.0.1:80"
    if r.exists(key_status):
        r.delete(key_status)
    r.set(key_status,json.dumps(jsonredis))#key值暂时先固定，如果有需要后边会进行改动
    # print("redis data",r.get("data"))

def results(ip,port,arguments,key_name):
    json_data={"status": "","msg":"","file":"","key":key_name}
    path = readpath()
    nm = nmap.PortScanner(nmap_search_path=('nmap', path))
    #暂时先写死，上边是通过读取文件的方法
    #nm = nmap.PortScanner(nmap_search_path=('nmap', r"C:\software\Nmap\nmap.exe"))
    results = nm.scan(ip, port, arguments)
    raw = nm.get_nmap_last_output()
    json_data["file"]=raw
    # saveraw(key_name,raw)  # 存储原先的数据为xml
    a = nm.command_line()
    # print(ip,port,arguments)
    # print(raw)
    print(a)
    # print(results)
    # 以下为协议的解析过程，解析到自己需要的数据,是通过得到的结果直接解析的
    # 通过判断scaninfo来判定这条语句是否成功
    info = results['nmap']['scaninfo']
    print("输出的info为",info)
    keys = list(info.keys())
    if keys[0] == 'error':
        json_data["status"] = '500'# 代表nmap语句执行失败
        msg=info[keys[0]]
        msg=msg[0]
        json_data["msg"]=msg
        print ("msg是",msg)
    else:
        json_data["status"] = '200' #代表nmap语句执行成功
        json_data["msg"]='该用例执行成功'
        # 只有在执行成功的时候才会保存端口信息
        # data222 = open("rawdata.xml").read() #验证data222和raw的数据是一样的
        # print("shuchu",data222)
        # root = parse("./rawdata.xml")
        # rootNode = root.documentElement
        # raw.documentElement
        root = et.fromstring(raw)
        print("root的根元素:", root.tag)
        # 查看有哪些子元素

        # for child_of_root in root:
        #     print (child_of_root.tag, child_of_root.attrib)
        #
        # for child_of_root in root[3]:
        #     print(child_of_root.tag, child_of_root.attrib)

        # t1 = root.findall("host")

        data_list = analysisxml(root)
        file_csv = "port.xls"
        print("data_list：", data_list)
        # Write_csv(file_csv,data_list)
        saveEXCEL(file_csv, data_list)
    # print(info)
    # print(keys[0])
    # print(results)
    id = '1'
    GMT_FORMAT = "%a %b %d %H:%M:%S %Y"
    timest = results['nmap']['scanstats']['elapsed']
    datetime1 = results['nmap']['scanstats']['timestr']
    time_format1 = datetime.strptime(datetime1, GMT_FORMAT)
    # print(time_format1)
    owner="1" #由服务端传入
    status="running"
    update_redis_status(status,owner)  # 将数据存入redis
    update_redis_abstract(key_name,id,timest, time_format1)  # 存储一些概要信息
    return json.dumps(json_data,ensure_ascii=False,default=str) #返回值
if __name__ == '__main__':

    ip='127.0.0.1'
    port='80-89'
    arguments='-Pn -sS -A'
    key_name="1_data"  #这个key是对应的redis的概要信息
    re=results(ip,port,arguments,key_name)
    print(re)






