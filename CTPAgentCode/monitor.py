#! /usr/bin/env python
# -*- coding: utf-8 -*-

import psutil
from datetime import datetime
import json

# CPU相关
def getTotal():
    cpu_percents = psutil.cpu_times_percent()

    scputimes= {
        'user' :cpu_percents.user,
        'system' :cpu_percents.system,
        'idle' :cpu_percents.idle,
        'interrupt' :cpu_percents.interrupt,
        'dpc' :cpu_percents.dpc,
    }
    s = json.dumps(scputimes);
    print(s)

    # 内存相关
    v_memory = psutil.virtual_memory()
    svmem={
        'total': v_memory.total,
        'available': v_memory.available,
        'percent': v_memory.percent,
        'used': v_memory.used,
        'free': v_memory.free
    }

    # 交换分区相关
    s_memory = psutil.swap_memory()
    sswap={
        'total':s_memory.total,
        'used':s_memory.used,
        'free':s_memory.free,
        'percent':s_memory.percent,
        'sin':s_memory.sin,
        'sout':s_memory.sout
    }

    # 硬盘相关
    disk = psutil.disk_io_counters()
    sdiskio={
        'read_count': disk.read_count,
        'write_count': disk.write_count,
        'read_bytes': disk.read_bytes,
        'write_bytes': disk.write_bytes,
        'read_time': disk.read_time,
        'write_time': disk.write_time,
    }

    # 网络相关
    net = psutil.net_io_counters()
    snetio = {
        'bytes_sent': net.bytes_sent,
        'bytes_recv': net.bytes_recv,
        'packets_sent': net.packets_sent,
        'packets_recv': net.packets_recv,
        'errin': net.errin,
        'errout': net.errout,
        'dropin': net.dropin,
        'dropout': net.dropout
    }

    # 服务器时间
    now = str(datetime.now()).split('.')[0]
    # print(now)

    payload = {'scputimes': scputimes, 'svmem': svmem, 'sswap': sswap, 'sdiskio': sdiskio, 'snetio': snetio, 'server_time': now}

    return payload

