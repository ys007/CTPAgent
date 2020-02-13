import yaml
import os
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
#- exec:
#   cmd: nmap -s -i

#解析后，第一层为list，第二层为dict

def getConfiger():
    # 获取当前脚本所在文件夹路径
    curPath = os.path.dirname(os.path.realpath(__file__))
    # 获取yaml文件路径
    yamlPath = os.path.join(curPath, "config.yaml")
    # 读取配置文件内容
    yaml_file = open(yamlPath, 'r', encoding='utf-8')
    data = yaml.load(yaml_file)
    print("data_type:", type(data))
    print("data_content:\n", data)
    #print("download_pwd", data['download']['password'])
    execYamlConfig(data)

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
            if k == 'exec':
                cmd = i['exec']['cmd']
                print('此处调用李帅印写的执行nmap代码，此代码需在成功后返回ok，当判断返回值为ok后才能执行后续的代码')
                break
            else:
                print(k)
                break


#if __name__ == '__main__':
#    getConfiger()