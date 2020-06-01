# -*- coding: utf-8 -*-
import os, socket
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

import logging
import logging.config

config = {    "key1":"value1"     }

log_path = "logger.conf"
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logger.conf')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger("agent")

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
         'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AGENT_IP = '192.168.23.23' #socket.gethostbyname(socket.gethostname()) #'172.31.28.239'
    AGENT_PORT = '5001'

    YAML_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"suiteConfig.yaml")

    REDIS_IP = '192.168.23.26'
    REDIS_PASSWORD = '123456'

    SVN_PATH = "D:\\Program Files\\TortoiseSVN\\bin"

    NMAP_PATH = "C:\\Program Files (x86)\\Nmap\\nmap.exe"
