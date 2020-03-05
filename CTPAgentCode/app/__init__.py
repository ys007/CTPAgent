from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config
import redis, json
from flask import Flask
from flask_executor import Executor

db = SQLAlchemy()
migrate = Migrate()
executor = Executor()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    executor.init_app(app)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    # f = open(r"redisIP.txt", "r")
    # line = f.readline()
    # redisIP = line.split(":")
    # app.config.REDIS_HOST = redisIP[0]
    # app.config.REDIS_IP = redisIP[1]
    # r = redis.StrictRedis(host=app.config.REDIS_HOS, db=0, password=app.config.REDIS_IP, decode_responses=True)
    # payload = {'type': 'security', 'subType': 'nmap', 'status': 'ready', 'owner': ''}
    # temp = json.dumps(payload)
    # statusKey = app.config.AGENT_IP + ':' + app.config.AGENT_PORT
    # r.lpush(statusKey, temp)

    return app


from app import models
