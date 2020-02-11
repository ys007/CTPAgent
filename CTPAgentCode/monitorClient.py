import socket
import json
from flask import Flask, request
import time
from concurrent.futures import ThreadPoolExecutor
import redis
import monitor
from times import sleeptime

executor = ThreadPoolExecutor()
app = Flask(__name__)
flag = 1
key = ''
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


if __name__ == '__main__':
    app.run(debug=True, port=5001, host=socket.gethostbyname(socket.gethostname()))