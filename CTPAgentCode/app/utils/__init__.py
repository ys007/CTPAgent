# import os, requests, pexpect,psutil,json,time
# from xml.etree import ElementTree as et
# from os.path import split
# from datetime import datetime
#
#
# def sleeptime(hour, min, sec):
#     return hour * 3600 + min * 60 + sec
#
#
# def sleeper(data, payload):
#     second = sleeptime(0, 0, data)
#     while 1 == 1:
#         time.sleep(second)
#         # r = redis.StrictRedis(host="127.0.0.1", port=6379, db=0)
#         # r.set('num', payload)  # 添加
#         print('do action')
#
#
#
# def git(url, file_name):
#     filename = os.path.join(os.getcwd(), file_name)
#     # url = 'https://raw.github.com/ys007/CTPAgent/master/CTPAgentCode/redisIP.txt'
#
#     r = requests.get(url)
#
#     with open(filename, 'wb') as f:
#         f.write(r.content)
#
#     # if os.path.exists()
#     print(os.getcwd() + "\\" + file_name)
#     if os.path.isfile(os.getcwd() + "\\" + file_name):
#         print("ok")
#         return "ok"
#     else:
#         print("fail")
#         return "fail"
#
#
# def svn(setting):
#     dist = setting['dist']
#     os.chdir(setting['svn'])
#     # 这里可能会出现换行情况
#     svn_url = setting['url']
#     svn_url = str(svn_url).replace("\n", "")
#     post = str(svn_url).rfind("/")
#     path = svn_url[post + 1:]
#     setting['url'] = svn_url
#     setting['dist'] = str(dist + "\\" + path)
#     cmd = 'svn export %(url)s %(dist)s --username %(user)s --password %(pwd)s' % setting
#     os.system(cmd)
#     print(dist)
#     if os.path.isfile(dist + "\\" + getConfig(svn_url)):
#         print("ok")
#         return "ok"
#     else:
#         print("fail")
#         return "fail"
#
#
# def getConfig(url):
#     return url.split("/")[-1]
#
#
#
# def svn_config():
#     SVN_username=''
#     SVN_password=''
#     SVN_path=''
#     nmap_path=''
#     config = open("config.xml").read()
#     root = et.fromstring(config)
#     for child_of_root in root:
#         if child_of_root.tag == 'messages':
#             for child_of_root2 in child_of_root:
#                 if child_of_root2.tag == 'message':
#                     SVN_username = child_of_root2.get('SVN_username')
#                     SVN_password = child_of_root2.get('SVN_password')
#         if child_of_root.tag == 'directions':
#             for child_of_root2 in child_of_root:
#                 if child_of_root2.tag == 'direction':
#                     SVN_path = child_of_root2.get('SVN_path')
#                     nmap_path = child_of_root2.get('nmap_path')
#                 # print(child_of_root2.tag, child_of_root2.attrib)
#     return SVN_username,SVN_password,SVN_path,nmap_path
#
#
# # CPU相关
# def get_status():
#     cpu_percents = psutil.cpu_times_percent()
#
#     scputimes= {
#         'user' :cpu_percents.user,
#         'system' :cpu_percents.system,
#         'idle' :cpu_percents.idle,
#         'interrupt' :cpu_percents.interrupt,
#         'dpc' :cpu_percents.dpc,
#     }
#     s = json.dumps(scputimes);
#     print(s)
#
#     # 内存相关
#     v_memory = psutil.virtual_memory()
#     svmem={
#         'total': v_memory.total,
#         'available': v_memory.available,
#         'percent': v_memory.percent,
#         'used': v_memory.used,
#         'free': v_memory.free
#     }
#
#     # 交换分区相关
#     s_memory = psutil.swap_memory()
#     sswap={
#         'total':s_memory.total,
#         'used':s_memory.used,
#         'free':s_memory.free,
#         'percent':s_memory.percent,
#         'sin':s_memory.sin,
#         'sout':s_memory.sout
#     }
#
#     # 硬盘相关
#     disk = psutil.disk_io_counters()
#     sdiskio={
#         'read_count': disk.read_count,
#         'write_count': disk.write_count,
#         'read_bytes': disk.read_bytes,
#         'write_bytes': disk.write_bytes,
#         'read_time': disk.read_time,
#         'write_time': disk.write_time,
#     }
#
#     # 网络相关
#     net = psutil.net_io_counters()
#     snetio = {
#         'bytes_sent': net.bytes_sent,
#         'bytes_recv': net.bytes_recv,
#         'packets_sent': net.packets_sent,
#         'packets_recv': net.packets_recv,
#         'errin': net.errin,
#         'errout': net.errout,
#         'dropin': net.dropin,
#         'dropout': net.dropout
#     }
#
#     # 服务器时间
#     now = str(datetime.now()).split('.')[0]
#     # print(now)
#
#     payload = {'scputimes': scputimes, 'svmem': svmem, 'sswap': sswap, 'sdiskio': sdiskio, 'snetio': snetio, 'server_time': now}
#
#     return payload
#
