import os
import requests
from flask import app
import urllib


# @app.route('/ready',methods=['get', 'post'])
# def ready():
#     return 'ok'
#
#
# @app.route('/git',method = ['get','post'])
# def git():
#     filename = os.path.join(os.getcwd(),'redisIP.txt')
#     url = 'https://raw.github.com/ys007/CTPAgent/master/CTPAgentCode/redisIP.txt'
#
#     r = requests.get(url)
#
#     with open(filename, 'wb') as f:
#         f.write(r.content)
#
#     return 'ok'
#
# @app.route('/svn',methods = ['get','post'])
# def svn():
#     url='svnurl'
#     fp = urllib.urlopen(url)
#     data = fp.read()
#     print(data)
# #无svn环境,待后续测试
#
#
# if __name__ == '__main__':
#     app.run(debug=True, port=5001, host=socket.gethostbyname(socket.gethostname()))


def git(url, file_name):
    filename = os.path.join(os.getcwd(), file_name)
    # url = 'https://raw.github.com/ys007/CTPAgent/master/CTPAgentCode/redisIP.txt'

    r = requests.get(url)

    with open(filename, 'wb') as f:
        f.write(r.content)
    return 'ok'


def svn(url, file_name):
    # url='svnurl'
    fp = urllib.urlopen(url)
    data = fp.read()
    print(data)
# 无svn环境,待后续测试
