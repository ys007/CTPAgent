import redis
import time


def sleeptime(hour, min, sec):
    return hour * 3600 + min * 60 + sec


def sleeper(data, payload):
    second = sleeptime(0, 0, data)
    while 1 == 1:
        time.sleep(second)
        # r = redis.StrictRedis(host="127.0.0.1", port=6379, db=0)
        # r.set('num', payload)  # 添加
        print('do action')

