import os
import requests
import config
from config import Config, logger
import redis, json

def git(url):
    # url = 'https://raw.githubusercontent.com/ys007/CTPAgent/master/CTPAgentCode/testConfig.yaml'
    file_name =getConfig(url)
    filename = os.path.join(os.getcwd(), file_name)
    r = requests.get(url)

    with open(filename, 'wb') as f:
        f.write(r.content)

    # if os.path.exists()
    print(os.getcwd()+"\\"+file_name)
    if os.path.isfile(os.getcwd()+"\\"+file_name):
        print("ok")
        return "ok"
    else:
        logger.error('git下载后没有找到该文件')
        print("fail")
        return "fail"

def svn(url):
    setting = {
        # svn 的本地安装路径
        'svn': Config.SVN_PATH,
        # 需要下载的svn文件
        "url": url,
        # svn账号
        "user": Config.SVN_USER,
        # svn密码
        "pwd": Config.SVN_PWD,
        # 下载到的路径
        "dist": config.basedir
    }
    dist = setting['dist']
    os.chdir(setting['svn'])
    # 这里可能会出现换行情况
    svn_url = setting['url']
    svn_url = str(svn_url).replace("\n", "")
    post = str(svn_url).rfind("/")
    path = svn_url[post + 1:]
    setting['url'] = svn_url
    setting['dist'] = str(dist + "\\" + path)
    cmd = 'svn export %(url)s %(dist)s --username %(user)s --password %(pwd)s' % setting
    os.system(cmd)
    print(dist)
    if os.path.isfile(dist + "\\" + getConfig(svn_url)):
        print("ok")
        return "ok"
    else:
        logger.error('svn下载后没有找到该文件')
        print("fail")
        return "fail"


def getConfig(url):
    return url.split("/")[-1]

#下载函数，mode 0：git；1：svn；
def download(mode, url):
    ret = 'fail'
    if mode == '0':
        ret = git(url)
    if mode == '1':
        ret = svn(url)
    return ret

#向redis发送信息的公共函数
def sendStatusToRedis(payload, mode='update'):
    r = redis.StrictRedis(host=Config.REDIS_IP, db=0, password=Config.REDIS_PASSWORD, decode_responses=True)
    if mode == 'update':
        temp = json.dumps(payload)
        statusKey = Config.AGENT_IP + ':' + Config.AGENT_PORT
        if r.exists(statusKey):
            r.delete(statusKey)
        r.set(statusKey, temp)
        print(temp)
        logger.info('发送到redis, 内容为：', temp)
    if mode == 'delete':
        r.delete(statusKey)
        logger.info('删除redis中的key', statusKey)
    return


if __name__ == '__main__':
    # 样例
    # 由于svn使用的是命令行,所以多了一个数据准备参数,需要写成如下方式
    # 且由于svn的更新方式导致下载文件名并不能更改
    setting = {
        # svn 的本地安装路径
        'svn': 'E:\\TortoiseSVN\\bin',
        # 需要下载的svn文件
        "url": 'https://39.97.104.82/svn/CTPDemo/gitUser.txt',
        # svn账号
        "user": 'caizhongbao',
        # svn密码
        "pwd": 'caizhongbao',
        # 下载到的路径
        "dist": "C:\\2.12"
    }
    # svn(setting=setting)
    # pass
    git('https://raw.githubusercontent.com/ys007/CTPAgent/master/CTPAgentCode/testConfig.yaml')