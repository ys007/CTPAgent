import os
#import requests  #这个是git下载用的
#import pexpect


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


#def git(url, file_name):
#    filename = os.path.join(os.getcwd(), file_name)
#    # url = 'https://raw.github.com/ys007/CTPAgent/master/CTPAgentCode/redisIP.txt'
#
#    r = requests.get(url)
#
#    with open(filename, 'wb') as f:
#        f.write(r.content)
#    return 'ok'

def svn(setting):
    dist = setting['dist']
    os.chdir(setting['svn'])
    # 这里可能会出现换行情况
    svn_url = setting['url']
    svn_url = str(svn_url).replace("\n", "")
    post = str(svn_url).rfind("/")
    path = svn_url[post + 1:]
    setting['url'] = svn_url
    setting['dist'] = str(dist + "\\" + path)
    # print(setting['dist'])
    cmd = 'svn export %(url)s %(dist)s --username %(user)s --password %(pwd)s' % setting
    os.system(cmd)


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
    svn(setting=setting)
    pass
