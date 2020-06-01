# -*- coding: utf-8 -*-
import yaml
import os
from app.utils.results import results, merge
from app.utils.util import download
import config
from config import Config, logger

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

#######################################################################

def DoTest(key, sequence, taskList):
    # 读取配置文件内容，配置文件yamlConfigFileHandle是在monitorClient中定义的
    logger.debug('调用DoTest函数')
    yaml_file = open(Config.YAML_FILE_PATH, 'r', encoding='utf-8')
    data = yaml.load(yaml_file)
    print("data_type:", type(data))
    print("data_content:\n", data['tasks'])
    taskID = "task" + sequence    #类似task1、task2
    task = data['tasks'][taskID]  #在yaml中该taskID中的所有内容

    return execYamlConfig(task, key, taskList)


#按照yaml文件中的配置项逐个执行，当前包括从配置库下载工具、执行nmap进行扫描
def execYamlConfig(task, key, taskList):
    ret = 'false'
    status = '500' #设置默认值为500，表示执行失败
    msg = '用例执行失败'
    resultFile = '' #执行结果的具体内容，用于返回给服务端使用
    time = ''  #nmap工具执行一条命令所用的时间，这个是命令执行后返回的
    joinType = getTaskKey(task, 'joinType')
    if joinType != 'easy':
        return {"status": '500', "msg": "该客户端不支持此种joinType！", "file": '', "key": key}

    print('此处调用才中宝写的代码，此代码需在成功后返回ok，当判断返回值为ok后才能执行后续的代码')
    setting = {
        # svn 的本地安装路径
        'svn': 'C:\\Program Files\\TortoiseSVN\\bin',
        # 需要下载的svn文件
        "url": getTaskKey(task, 'url'),
        # svn账号
        "user": getTaskKey(task, 'username'),
        # svn密码
        "pwd": getTaskKey(task, 'password'),
        # 下载到的路径
        "dist": config.basedir
    }

    ret = 'ok'  # 为了调试，临时改成这样##############################################################################################
    # ret = download('1', getTaskKey(task, 'url'), getTaskKey(task, 'username'), getTaskKey(task, 'password'))
    if ret != 'ok':
        print('从配置库获取工具失败，无法执行后续测试！')
        logger.error('从配置库获取工具失败，无法执行后续测试！')
        return {"status": '500', "msg": "从配置库获取工具失败，无法执行后续测试！", "file": '', "key": key}
    else:
        logger.info("工具下载完成")

    #如果taskList的值为空，则根据isDetail和content的值拼接出任务去执行
    if len(taskList) == 0:
        return dealDetailAndContent(task, key)
    #如果taskList的内容不为空，那就要根据taskList里的值，在用content的公式拼接出任务去执行
    else:
        return dealTaskList(task, taskList, key)

################################################
# 当服务端的post的taskList为空时，进入此函数，如果isDetail为y，则直接根据content的内容依照ip合并后进行测试
# 否则，content的内容为公式，x是range，y是subrange，去拼接ip和port，然后进行测试
################################################
def dealDetailAndContent(taskContent, key):
    print("in dealDetailAndContent")
    try:
        arguments = getTaskKey(taskContent, 'arguments')
        content = getTaskKey(taskContent, 'content')[0].lower()

        #如果isDetail为n，表示需要拼接，需将range和subrange中的内容拼接到content中的x、y处，组成ip：port样式
        if (getTaskKey(taskContent, 'isDetail') == 'n'):
            ip, port = getIpAndPortFromContent(content, getTaskKey(taskContent, 'range'), getTaskKey(taskContent, 'subRange'))
            # 此函数当前的返回值为执行结果
            status, msg, resultFile, time = results(ip, port, arguments)
            return {"status": status, "msg": msg, "file": resultFile, "key": key}

        #如果isDetal为y，表示不需要拼接，直接解析content中的内容，作为ip：port，进行测试
        elif(getTaskKey(taskContent, 'isDetail') == 'y'):
            status = '200'  # status是最终的测试结果，statusOnce是单次的测试结果
            msg = "该用例执行成功"
            resultFile = ""
            taskIpPortList = {}
            addrList = getTaskKey(taskContent, 'content')
            arguments = getTaskKey(taskContent, 'arguments')
            for addr in addrList:
                print('addr: ', addr)
                ip = addr[0: addr.index(':')]
                port = addr[addr.index(':') + 1:]
                print(ip, port)
                if ip in taskIpPortList.keys():
                    taskIpPortList[ip] = '{0},{1}'.format(taskIpPortList[ip], port)
                else:
                    taskIpPortList[ip] = port

            status, msg, resultFile = testFromList(taskIpPortList, arguments)

            return {"status": status, "msg": msg, "file": resultFile, "key": key}

            mode = taskContent['subtype']
        else:
            logger.error("yaml中的任务中的字段【isDetail】值填写有误！")
            return {"status": "500", "msg": "yaml中的字段【isDetail】值填写有误", "file": "", "key": key}

    except Exception:
        print("获取yaml字段异常！")
        logger.critical("获取yaml字段异常！")
        return {"status": '500', "msg": "获取yaml字段异常，无法执行后续测试！", "file": '', "key": key}

################################################
#当服务端的post的taskList不为空时，进入此函数，根据content字段的公式，对taskList的值进行拼接，最终得到测试的ip和port，并执行扫描，返回结果
################################################
def dealTaskList(taskContent, taskList, key):
    print("in dealTaskList")
    status = '200'
    msg = "该用例执行成功"
    resultFile = ''
    taskIpPortList = {}

    arguments = getTaskKey(taskContent, 'arguments')
    content = getTaskKey(taskContent, 'content')[0].lower()
    lastIp = content[content.rindex(':') - 1: content.rindex(':')]
    contentPort = content[content.rindex(':') + 1:]
    if (lastIp.isdigit() or contentPort.isdigit()):
        #如果content中的公式只有一个变量，则把taskList中的值直接替换了该变量，然后得到ip和port，调用nmap扫描函数
        ip, port = getIpAndPortFromContent(content, ','.join(taskList), ','.join(taskList))
        status, msg, resultFile, time = results(ip, port, arguments)

    else:
        # 如果content中的公式有两个变量，ip和port都存在变量，那么需要把taskList进行解析，把相同ip的端口都合并，然后每一个ip调一遍nmap扫描函数
        for task in taskList:
            taskip = content[0:content.rindex('.') + 1] + task.split('-')[0]
            taskport = task.split('-')[1]

            if taskip in taskIpPortList.keys():
                taskIpPortList[taskip] = '{0},{1}'.format(taskIpPortList[taskip], taskport)
            else:
                taskIpPortList[taskip] = taskport

        status, msg, resultFile = testFromList(taskIpPortList, arguments)
    return {"status": status, "msg": msg, "file": resultFile, "key": key}

################################################
#根据传入的ipPortList和arguments调用nmap函数进行测试，并在每次测试之后组装测试结果resultFile
################################################
def testFromList(ipPortList, arguments):
    status = '200'
    msg = "该用例执行成功"
    resultFile = ''

    for task in ipPortList:
        # 最终得到IP和port
        ip = task
        port = ipPortList[ip]
        statusOnce, msgOnce, resultFileOnce, timeOnce = results(ip, port, arguments)
        if status == '500' or statusOnce == '500':
            status = '500'
            msg = msgOnce
        resultFile = merge(resultFileOnce, resultFile)
    return status, msg, resultFile

################################################
#解析content字段，从中获得ip和port字段，用于后续调用nmap扫描函数
################################################
def getIpAndPortFromContent(content, x, y):
    #把公式中的x和y进行替换
    contentNew = content.replace('x', x)
    contentNew = contentNew.replace('y', y)
    #最终得到IP和port
    ip = contentNew[0 : contentNew.rindex(':')]
    port = contentNew[contentNew.rindex(':') + 1:]
    return ip, port

################################################
#获取yaml文件中的task下的某个字段的值，由于该字段可能不存在，故在此函数中会判断，如果存在此字段，返回该字段的值，如果不存在，返回空
#最初的时候该函数在没有此字段时返回error，切报异常，但是在代码中的其他地方调用的时候有不存在也调用的情况，故改为了返回空值
################################################
def getTaskKey(task, dictKey):
    if dictKey in task.keys():
        return task[dictKey]
    else:
        logger.info("yaml文件中没有字段【%s】", dictKey)
        return ""

#if __name__ == '__main__':
#    getConfiger()