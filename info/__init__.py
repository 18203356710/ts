from flask import Flask,session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from config import config_dict,Config
# 日志信息
import logging
from logging.handlers import RotatingFileHandler

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)
# 创建日志记录器
file_log_handler=RotatingFileHandler('logs/loga',maxBytes=1024*1024*100,backupCount=10)
# 创建日志的格式
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)
from redis import StrictRedis
redis_store=StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)
db=SQLAlchemy()
from flask_wtf import CSRFProtect,csrf
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    #登录注册
    from info.modules.login import login_blue
    app.register_blueprint(login_blue)
    # 房屋蓝图
    from info.modules.house import house_blue
    app.register_blueprint(house_blue)
    # 用户蓝图
    from info.modules.user import user_blue
    app.register_blueprint(user_blue)
    # 订单蓝图
    from info.modules.order import order_blue
    app.register_blueprint(order_blue)

    # CSRFProtect(app)
    # @app.after_request
    # def after_request(response):
    #     csrf_token=csrf.generate_csrf()
    #     response.set_cookie('csrf_token',csrf_token)
    #     return response

    return app