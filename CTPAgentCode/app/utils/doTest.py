import yaml
import os
from app.utils.results import results
from app.utils.download import git,svn
import config
from config import Config

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

#yaml配置文件的格式为：
#- download:
#   mode: git
#   url: http://192.168.23.14/svn/工具/nmap
#- download:
#   mode: svn
#   url: http://192.168.23.14/svn/工具/nmap
#   username: root
#   password: 123
#- test:
#   mode: nmap
#   ip: 127.0.0.1
#   port: 80 - 89
#   arguments: -Pn - sS - A
#- test:
#   mode: nmap
#   ip: ...
#   port: ...
#   arguments: ...

#解析后，第一层为list，第二层为dict

def DoTest(key):
    # 读取配置文件内容，配置文件yamlConfigFileHandle是在monitorClient中定义的
    yaml_file = open(Config.YAML_FILE_PATH, 'r', encoding='utf-8')
    data = yaml.load(yaml_file)
    print("data_type:", type(data))
    print("data_content:\n", data)
    #print("download_pwd", data['download']['password'])
    return execYamlConfig(data, key)

#按照yaml文件中的配置项逐个执行，当前包括从配置库下载工具、执行nmap进行扫描
def execYamlConfig(list_a, key):
    ret = 'false'
    status = '500' #设置默认值为500，表示执行失败
    msg = '用例执行失败'
    resultFile = '' #执行结果的具体内容，用于返回给服务端使用
    time = ''  #nmap工具执行一条命令所用的时间，这个是命令执行后返回的

    for i in list_a:
        print("list[%s]=" % i)

        for (k, v) in i.items():
            print("dict[%s]=" % k, v)
            if k == 'download':
                mode = i['download']['mode']
                url = i['download']['url']
                print('此处调用才中宝写的代码，此代码需在成功后返回ok，当判断返回值为ok后才能执行后续的代码')
                if mode == 'git':
                    ret = git(url)

                if mode == 'svn':
                    setting = {
                        # svn 的本地安装路径
                        'svn': 'C:\\Program Files\\TortoiseSVN\\bin',
                        # 需要下载的svn文件
                        "url": url,
                        # svn账号
                        "user": 'caizhongbao',
                        # svn密码
                        "pwd": 'caizhongbao',
                        # 下载到的路径
                        "dist": config.basedir
                    }
                    # os.rename(image, new_file)
                    ret = svn(setting=setting)

                if ret == 'ok':
                    break

                else:
                    print('从配置库获取工具失败，无法执行后续测试！')
                    return {"status": '500', "msg": "从配置库获取工具失败，无法执行后续测试！", "file": '', "key": key}

            if k == 'test':
                mode = i['test']['subtype']
                if mode == 'nmap':
                    print('此处调用李帅印写的执行nmap代码，此代码需在成功后返回ok，当判断返回值为ok后才能执行后续的代码')
                    ip = i['test']['ip']
                    port = i['test']['port']
                    arguments = i['test']['arguments']

                    # 此函数当前的返回值为执行结果，需要改一下，返回是否执行成功，当前返回的值作为全局变量使用
                    status, msg, resultFile, time = results(ip, port, arguments)
                break
            else:
                print(k)
                break

    return {"status": status, "msg": msg, "file": resultFile, "key": key}

#if __name__ == '__main__':
#    getConfiger()