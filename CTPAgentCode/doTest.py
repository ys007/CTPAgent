import yaml
import os
from results import results
from monitorClient import yamlConfigFileHandle
import globalvar as gl

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

gl._init()  # 初始化全局变量管理模块

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
gl._init()  # 初始化全局变量管理模块
def DoTest():
    # 读取配置文件内容，配置文件yamlConfigFileHandle是在monitorClient中定义的
    yaml_file = open(yamlConfigFileHandle, 'r', encoding='utf-8')
    data = yaml.load(yaml_file)
    print("data_type:", type(data))
    print("data_content:\n", data)
    #print("download_pwd", data['download']['password'])
    execYamlConfig(data)

#按照yaml文件中的配置项逐个执行，当前包括从配置库下载工具、执行nmap进行扫描
def execYamlConfig(list_a):
    for i in list_a:
        print("list[%s]=" % i)

        for (k, v) in i.items():
            print("dict[%s]=" % k, v)
            if k == 'download':
                mode = i['download']['mode']
                url = i['download']['url']
                print('此处调用才中宝写的代码，此代码需在成功后返回ok，当判断返回值为ok后才能执行后续的代码')
                break
            if k == 'test':
                mode = i['test']['mode']
                if mode == 'nmap':
                    print('此处调用李帅印写的执行nmap代码，此代码需在成功后返回ok，当判断返回值为ok后才能执行后续的代码')
                    ip = i['test']['ip']
                    port = i['test']['port']
                    arguments = i['test']['arguments']

                    # 此函数当前的返回值为执行结果，需要改一下，返回是否执行成功，当前返回的值作为全局变量使用
                    ret = results(ip, port, arguments, gl.get_value('key2'))
                break
            else:
                print(k)
                break
    gl.set_value('testResult', ret)  # 设置变量值 testResult，用于发送到redis
    return gl.get_value('testResult')

#if __name__ == '__main__':
#    getConfiger()