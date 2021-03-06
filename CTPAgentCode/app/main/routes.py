import os
import time,json
from app import db,executor
import app
from app.main import bp
from flask import render_template, session, jsonify, g, flash, redirect, url_for, Response, send_file, request
# from times import sleeptime
from config import Config, logger
from app.utils.doTest import DoTest
from app.utils.util import download, sendStatusToRedis
from concurrent.futures import ThreadPoolExecutor
import atexit

owner = ''
#程序启动后即调用此函数，向redis上报本机状态
def pushStatusIdle():
    logger.debug('程序启动，向redis上报自己的状态')
    print('程序启动上报redis自己的状态')
    payload = {'type': 'security', 'subType': 'nmap', 'status': 'idle', 'owner': ''}
    try:
        sendStatusToRedis(payload)
    except Exception:
        print ("向redis发送函数异常！")
        logger.critical("向redis发送函数异常，程序即将退出")
        exit(0)

pushStatusIdle()

@bp.before_app_request
def before_request():
    g.statusKey = Config.AGENT_IP + ':' + Config.AGENT_PORT

###############################################################################################
# 准备接口：agent去指定配置库中获取yaml测试文件等各种文件【文件url服务端会传入】，以及agent自身需要准备的任务。
# 该接口有五个参数：
# 1、测试文件url（fileurl）
# 2、配置库类型（repository：'0'：git、'1'：svn、'2'：cvs）
# 3、配置库用户名（repousername）
# 4、配置库密码（repopassword）
# 5、所有者（owner）
###############################################################################################
@bp.route('/suiteReady', methods=['get', 'post'])
def suiteReady():
    logger.debug('收到suiteReady指令，进入suiteReady函数')
    ret = 'false'
    print('在suiteReady分支里面')
    global owner
    jsonstr = request.json
    fileurl = jsonstr.get("fileurl")
    print('yaml文件地址：%s', fileurl)
    repository = jsonstr.get("repository")
    repousername = jsonstr.get("repousername")
    repopassword = jsonstr.get("repopassword")
    if owner == '':
        owner = jsonstr.get("owner")

    #下载模式字段，需要根据和服务端的调试情况来调整
    try:
        ret = download(repository, fileurl, repousername, repopassword)
    except Exception:
        print ("下载异常！")
        logger.critical("下载出现异常，程序即将退出")
        exit(0)
    else:
        if ret == 'ok':
            payload = {'type': 'security', 'subType':'nmap', 'status':'ready', 'owner': owner}
            sendStatusToRedis(payload)
            return {"status": '200', "msg": '执行成功'}
        else:
            return {"status": '500', "msg": '执行失败'}

###############################################################################################
# 执行接口：agent根据之前获取的yaml测试文件执行测试并将测试结果写入redis【redis的key由服务端传入】
# 该接口有一下三个参数：
# 1、任务序号（sequence）
# 2、任务列表（taskList：[ ]）【若不需要拆分，则为空】
# 3、测试结果key（key）【汇总类型的测试结果写入redis】
###############################################################################################
@bp.route('/suiteRun', methods=['get', 'post'])
def suiteRun():
    logger.debug('收到suiteRun指令，进入suiteRun函数')
    print('进入执行分支')
    global flag, owner
    flag = 1
    jsonstr = request.json
    g.sequence = jsonstr.get("sequence")
    g.taskList = jsonstr.get("taskList")
    g.key = jsonstr.get("key")
    print('准备传递的key:',g.key)

    #开始执行测试，向redis发送running状态
    try:
        payload = {'type': 'security', 'subType': 'nmap', 'status': 'running', 'owner': owner}
        sendStatusToRedis(payload)
        print("开始执行测试")
        executor = ThreadPoolExecutor()
        task = executor.submit(do_update, g.key, g.sequence, g.taskList)

        #向redis发送实时状态，测试执行完，实时状态变为idle
        owner = ''
        payload = {'type': 'security', 'subType': 'nmap', 'status': 'idle', 'owner': owner}
        sendStatusToRedis(payload)
        print(task.result())
        return task.result()
    except Exception:
        print ("执行测试过程出现异常！")
        logger.critical("执行测试过程出现异常，程序即将退出")
        exit(0)

def do_update(key, sequence, taskList):
    print('在do_update分支里面')
    global flag
    while True:
        if flag == 0:
            break

        #执行测试，返回的就是给post的返回值
        try:
            return DoTest(key, sequence, taskList)
        except Exception:
            print ("执行测试异常！")
            logger.critical("执行测试异常，程序即将退出")
            exit(0)

###############################################################################################
# 取消接口：agent删除之前获取的yaml测试文件，并进行本地的一些退出测试的操作。
# 本接口没有参数
###############################################################################################
@bp.route('/suiteCancel', methods=['get', 'post'])
def suiteCancel():
    logger.debug('收到cancel指令，进入cancel函数')
    print ('进入取消分支')
    try:
        global  owner
        #1、删除yaml文件
        if os.path.exists(Config.YAML_FILE_PATH):  # 如果文件存在
            #1、删除文件
            os.remove(Config.YAML_FILE_PATH)

            #2、上报本机状态
            owner = ''
            payload = {'type': 'security', 'subType':'nmap', 'status':'idle', 'owner': owner}
            sendStatusToRedis(payload)
            return {"status": '200', "msg": '执行成功'}

        else:
            print('no such file:%s' %Config.YAML_FILE_PATH)  # 否则，返回文件不存在
            return {"status": '500', "msg": '删除失败：没有测试yaml文件'}
    except Exception:
        print("取消接口执行异常！")
        logger.critical("取消接口执行异常，程序即将退出")
        exit(0)

#程序正常退出前执行此函数，删除redis中状态信息，如果程序异常退出则不执行此函数
def deleteRedisStatus():
    sendStatusToRedis('none', 'delete')
    logger.debug('正常退出，删除redis中的状态信息')
    print ('正常退出，删除redis中的状态信息')

atexit.register(deleteRedisStatus)

