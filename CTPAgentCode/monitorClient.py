import socket
import json
from flask import Flask, request
from concurrent.futures import ThreadPoolExecutor
import redis
import os
import doTest
from download import svn
from download import git
import globalvar as gl
import atexit

gl._init()  # 初始化全局变量管理模块

app = Flask(__name__)
flag = 1

#本地IP
agentIP = socket.gethostbyname(socket.gethostname())
#本程序运行端口号
agentPort = '5001'

# 获取当前脚本所在文件夹路径，这个路径是文件夹的路径，不带文件名
workspacePath = os.path.dirname(os.path.realpath(__file__))  #add by cjj
yamlConfigFileHandle = os.path.join(workspacePath, "testConfig.yaml")  #add by cjj  待和服务端确定好了yaml文件的名字和传给我的方式后，这个地方需要修改一下，但是这个字段名字需要保留
#end add by cjj

def readIP():
    f = open(r"redisIP.txt","r")
    line = f.readline()
    redisIP = line.split(":")
    return redisIP

#begin add by cjj
#向redis发送信息的公共函数
def sendStatusToRedis(payload, mode='update'):
    r = redis.StrictRedis(host=readIP()[0], db=0, password=readIP()[1], decode_responses=True)
    if mode == 'update':
        temp = json.dumps(payload)
        statusKey = agentIP + ':' + agentPort
        if r.exists(statusKey):
            r.delete(statusKey)
        r.set(statusKey, temp)
        print(temp)
    if mode == 'delete':
        r.delete(statusKey)

    return

#程序启动后即调用此函数，向redis上报本机状态
def pushStatusIdle():
    payload = {'type': 'security', 'subType': 'nmap', 'status': 'idle', 'owner': ''}
    sendStatusToRedis(payload)

#准备接口：agent去指定配置库中获取yaml测试文件【文件url服务端会传入】，以及agent自身需要准备的任务。
@app.route('/ready', methods=['get', 'post'])
def ready():
    global owner
    jsonstr = request.json
    fileurl = jsonstr.get("fileurl")
    repository = jsonstr.get("repository")
    owner = jsonstr.get("owner")

    if repository == '0': #git
        #这里需要调用才中宝写的git下载函数，该函数目前有问题，调通后再打开   ?????????????????????????????????????????????????????????????????????????????????????
        #git(fileurl)
        payload = {'type': 'security', 'subType': 'nmap', 'status': 'ready', 'owner': owner}
        sendStatusToRedis(payload)
        return {"status": '200', "msg": '执行成功'}

    #下载模式字段，需要根据和服务端的调试情况来调整
    if repository == '1': #svn
        #这里调用才中宝的代码下载yaml文件，文件下载后的保存路径为workspacePath
        setting = {
            # svn 的本地安装路径
            'svn': 'C:\\Program Files\\TortoiseSVN\\bin',
            # 需要下载的svn文件
            "url": fileurl,  #'https://39.97.104.82/svn/CTPDemo/gitUser.txt'  #这个地方需要和服务端确认，文件的名字是在url中传过来还是一个单独的参数？？？？？？？
            # svn账号
            "user": 'caizhongbao',
            # svn密码
            "pwd": 'caizhongbao',
            # 下载到的路径
            "dist": workspacePath
        }

        ret = svn(setting = setting) #这个函数目前没有返回值，需要加返回值，如果确实下载下来了文件，返回ok，否则返回false
        if ret == 'ok':
            payload = {'type': 'security', 'subType':'nmap', 'status':'ready', 'owner': owner}
            sendStatusToRedis(payload)
            return {"status": '200', "msg": '执行成功'}
        else:
            return {"status": '500', "msg": '执行失败'}


#执行接口：agent根据之前获取的yaml测试文件执行测试并将测试结果写入redis【redis的key由服务端传入】
@app.route('/run', methods=['get', 'post'])
def run():
    print('进入执行分支')
    executor = ThreadPoolExecutor()
    global flag
    flag = 1
    jsonstr = request.json
    gl.set_value('key', jsonstr.get("key"))  # 设置变量值 key的值

    #开始执行测试，向redis发送running状态
    payload = {'type': 'security', 'subType': 'nmap', 'status': 'running', 'owner': owner}
    sendStatusToRedis(payload)
    #r.delete(gl.get_value('key'))
    print("开始执行测试")
    task = executor.submit(do_update)

    #向redis发送实时状态，测试执行完，实时状态变为idle
    payload = {'type': 'security', 'subType': 'nmap', 'status': 'idle', 'owner': ''}
    sendStatusToRedis(payload)
    print(task.result())
    return task.result()


def do_update():
    global flag
    while True:
        if flag == 0:
            break

        #执行测试，返回的就是给post的返回值
        return doTest.DoTest()

#取消接口：agent删除之前获取的yaml测试文件。
@app.route('/cancel', methods=['get', 'post'])
def cancel():
    print ('进入取消分支')
    #1、删除yaml文件
    if os.path.exists(yamlConfigFileHandle):  # 如果文件存在
        # 删除文件
        os.remove(yamlConfigFileHandle)

        #2、上报本机状态
        payload = {'type': 'security', 'subType':'nmap', 'status':'idle', 'owner': ''}
        sendStatusToRedis(payload)
        return {"status": '200', "msg": '执行成功'}

    else:
        print('no such file:%s' %yamlConfigFileHandle)  # 否则，返回文件不存在
        return {"status": '500', "msg": '删除失败：没有测试yaml文件'}

#程序正常退出前执行此函数，删除redis中状态信息，如果程序异常退出则不执行此函数
def deleteRedisStatus():
    sendStatusToRedis('none', 'delete')
    print ('正常退出，删除redis中的状态信息')

atexit.register(deleteRedisStatus)

#end add by cjj

if __name__ == '__main__':
    pushStatusIdle()
    app.run(debug=True, port=agentPort, host=agentIP)