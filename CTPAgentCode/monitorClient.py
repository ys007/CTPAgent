import socket
import json
from flask import Flask, request
import time
from concurrent.futures import ThreadPoolExecutor
import redis
import monitor
from times import sleeptime

#begin add by cjj
import os
import doTest
from download import svn
import globalvar as gl

gl._init()  # 初始化全局变量管理模块

gl.set_value('key1', '0')  # 设置变量值 key1 = '0'
gl.set_value('key2', '0')  # 设置变量值 key2 = '0'
executor = ThreadPoolExecutor()
app = Flask(__name__)
flag = 1
#key = ''

# 获取当前脚本所在文件夹路径，这个路径是文件夹的路径，不带文件名
yamlConfigFilePath = os.path.dirname(os.path.realpath(__file__))  #add by cjj
yamlConfigFileHandle = os.path.join(yamlConfigFilePath, "config.yaml")  #add by cjj  待和服务端确定好了yaml文件的名字和传给我的方式后，这个地方需要修改一下，但是这个字段名字需要保留
#end add by cjj

@app.route('/start', methods=['get', 'post'])
def update_redis():
    global executor
    executor= ThreadPoolExecutor()
    global flag
    flag =1
    jsonstr = request.json
    global key
    key = jsonstr.get("key")
    # key = "9_26_172.31.3.182_perf"
    # key = "9_26_172.31.3.188_perf"
    # key = "9_4_172.31.3.182_perf"
    # redisIP = readIP()[0]
    # redisPSW = readIP()[1]
    # print(redisIP+redisPSW)
    global res
    res = sleeptime(0, 0, int(jsonstr.get('frequency')))
    # res = 1
    r = redis.StrictRedis(host=readIP()[0], db=0, password=readIP()[1], decode_responses=True)
    r.delete(key)
    print("开始执行")
    executor.submit(do_update)
    return 'ok'


def do_update():
    global key, res, flag
    r = redis.StrictRedis(host=readIP()[0], db=0, password=readIP()[1], decode_responses=True)
    while True:
        if flag == 0:
            break
        time.sleep(res)
        payload = monitor.getTotal()
        temp = json.dumps(payload)
        r.lpush(key, temp)
        print(temp)


@app.route('/end', methods=['get', 'post'])
def end():
    global flag
    flag =0
    executor.shutdown()
    print("结束写入")
    return "ok"


def readIP():
    f = open(r"redisIP.txt","r")
    line = f.readline()
    redisIP = line.split(":")
    return redisIP

#begin add by cjj


#准备接口：agent去指定配置库中获取yaml测试文件【文件url服务端会传入】，以及agent自身需要准备的任务。
@app.route('/prepare', methods=['get', 'post'])
def prepare():
    jsonstr = request.json
    url = jsonstr.get("fileurl")

    #下载模式字段，需要根据和服务端的调试情况来调整
    mode = "git"

    #这里调用才中宝的代码下载yaml文件，文件下载后的保存路径为yamlConfigFilePath
    setting = {
        # svn 的本地安装路径
        'svn': 'C:\\Program Files\\TortoiseSVN\\bin',
        # 需要下载的svn文件
        "url": url,  #'https://39.97.104.82/svn/CTPDemo/gitUser.txt'  #这个地方需要和服务端确认，文件的名字是在url中传过来还是一个单独的参数？？？？？？？
        # svn账号
        "user": 'caizhongbao',
        # svn密码
        "pwd": 'caizhongbao',
        # 下载到的路径
        "dist": yamlConfigFilePath
    }
    svn(setting = setting)  #这个函数目前没有返回值，需要加返回值，如果确实下载下来了文件，返回ok，否则返回false

    #os.rename(image, new_file)


#执行接口：agent根据之前获取的yaml测试文件执行测试并将测试结果写入redis【redis的key由服务端传入】
@app.route('/run', methods=['get', 'post'])
def run():
    global executor
    executor = ThreadPoolExecutor()
    global flag
    flag = 1
    jsonstr = request.json
    gl.set_value('key1', jsonstr.get("key1"))  # 设置变量值 key1的值
    gl.set_value('key2', jsonstr.get("key2"))  # 设置变量值 key2的值
    global r
    r = redis.StrictRedis(host=readIP()[0], db=0, password=readIP()[1], decode_responses=True)
    r.delete(gl.get_value('key1'))
    r.delete(gl.get_value('key2'))
    print("开始执行")
    executor.submit(do_update)
    return 'ok'


def do_update():
    global flag, r
    r = redis.StrictRedis(host=readIP()[0], db=0, password=readIP()[1], decode_responses=True)
    while True:
        if flag == 0:
            break
        #time.sleep(res)
        #下面这几句是从李帅印的代码中得到发送给redis的内容
        ret = doTest.DoTest()
        if ret == 'ok':
            temp = json.dumps(gl.get_value('testResult'))
            r.lpush(gl.get_value('key2'), temp)
            print(temp)

#取消接口：agent删除之前获取的yaml测试文件。
app.route('/cancel', methods=['get', 'post'])
def cancel():

    if os.path.exists(yamlConfigFileHandle):  # 如果文件存在
        # 删除文件
        os.remove(yamlConfigFileHandle)
        return 'ok'
    else:
        print('no such file:%s' %yamlConfigFileHandle)  # 否则，返回文件不存在
        return 'no such file'
    
#end add by cjj

if __name__ == '__main__':
    app.run(debug=True, port=5001, host=socket.gethostbyname(socket.gethostname()))