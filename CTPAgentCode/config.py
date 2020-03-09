import os, socket
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
         'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AGENT_IP = socket.gethostbyname(socket.gethostname())
    AGENT_PORT = '5001'

    YAML_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),"testConfig.yaml")

    REDIS_IP = '127.0.0.1'
    REDIS_PASSWORD = 'Aisino_u3'

    SVN_PATH = "C:\\Program Files\\TortoiseSVN\\bin"
    SVN_USER = 'caizhongbao'
    SVN_PWD = 'caizhongbao'

    NMAP_PATH = "C:\\Program Files (x86)\\Nmap\\nmap.exe"
