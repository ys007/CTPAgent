import os
import time,json
from app import db,executor
import app
from app.main import bp
from flask import render_template, session, jsonify, g, flash, redirect, url_for, Response, send_file, request
# from times import sleeptime
import config
from config import Config
from app.utils.doTest import DoTest
from app.utils.util import download, sendStatusToRedis
from concurrent.futures import ThreadPoolExecutor
import atexit


#程序启动后即调用此函数，向redis上报本机状态
def pushStatusIdle():
    print('程序启动上报redis自己的状态')
    payload = {'type': 'security', 'subType': 'nmap', 'status': 'idle', 'owner': ''}
    sendStatusToRedis(payload)
pushStatusIdle()

@bp.before_app_request
def before_request():
    g.statusKey = Config.AGENT_IP + ':' + Config.AGENT_PORT


#准备接口：agent去指定配置库中获取yaml测试文件【文件url服务端会传入】，以及agent自身需要准备的任务。
@bp.route('/ready', methods=['get', 'post'])
def ready():
    ret = 'false'
    print('在ready分支里面')
    global owner
    jsonstr = request.json
    fileurl = jsonstr.get("fileurl")
    repository = jsonstr.get("repository")
    owner = jsonstr.get("owner")

    #下载模式字段，需要根据和服务端的调试情况来调整
    ret = download(repository, fileurl)

    if ret == 'ok':
        payload = {'type': 'security', 'subType':'nmap', 'status':'ready', 'owner': owner}
        sendStatusToRedis(payload)
        return {"status": '200', "msg": '执行成功'}
    else:
        return {"status": '500', "msg": '执行失败'}


#执行接口：agent根据之前获取的yaml测试文件执行测试并将测试结果写入redis【redis的key由服务端传入】
@bp.route('/run', methods=['get', 'post'])
def run():
    print('进入执行分支')
    executor = ThreadPoolExecutor()
    global flag
    flag = 1
    jsonstr = request.json
    g.key = jsonstr.get("key")
    print('准备传递的key:',g.key)

    #开始执行测试，向redis发送running状态
    payload = {'type': 'security', 'subType': 'nmap', 'status': 'running', 'owner': owner}
    sendStatusToRedis(payload)
    print("开始执行测试")
    task = executor.submit(do_update, (g.key))

    #向redis发送实时状态，测试执行完，实时状态变为idle
    payload = {'type': 'security', 'subType': 'nmap', 'status': 'idle', 'owner': ''}
    sendStatusToRedis(payload)
    print(task.result())
    return task.result()


def do_update(key):
    print('在do_update分支里面')
    global flag
    while True:
        if flag == 0:
            break

        #执行测试，返回的就是给post的返回值
        return DoTest(key)

#取消接口：agent删除之前获取的yaml测试文件。
@bp.route('/cancel', methods=['get', 'post'])
def cancel():
    print ('进入取消分支')
    #1、删除yaml文件
    if os.path.exists(Config.YAML_FILE_PATH):  # 如果文件存在
        # 删除文件
        os.remove(Config.YAML_FILE_PATH)

        #2、上报本机状态
        payload = {'type': 'security', 'subType':'nmap', 'status':'idle', 'owner': ''}
        sendStatusToRedis(payload)
        return {"status": '200', "msg": '执行成功'}

    else:
        print('no such file:%s' %Config.YAML_FILE_PATH)  # 否则，返回文件不存在
        return {"status": '500', "msg": '删除失败：没有测试yaml文件'}

#程序正常退出前执行此函数，删除redis中状态信息，如果程序异常退出则不执行此函数
def deleteRedisStatus():
    sendStatusToRedis('none', 'delete')
    print ('正常退出，删除redis中的状态信息')

atexit.register(deleteRedisStatus)

