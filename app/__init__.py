from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
import pymysql

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    
    # 配置CORS - 允许所有域名访问
    CORS(app, resources={
        r"*": {
            "origins": "*",  # 允许所有域名访问
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })
    
    # 数据库和表结构由MySQL容器通过init.sql自动创建
    
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.chat import bp as chat_bp
    app.register_blueprint(chat_bp, url_prefix='/chat')
    
    from app.model import bp as model_bp
    app.register_blueprint(model_bp, url_prefix='/model')
    
    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')
    
    from app.repository import bp as repository_bp
    app.register_blueprint(repository_bp, url_prefix='/repository')
    
    # 在应用上下文中导入 User 模型
    with app.app_context():
        from app.models import User
        
        @jwt.user_identity_loader
        def user_identity_lookup(user):
            return str(user.id)  # 返回字符串类型的用户 ID
        
        @jwt.user_lookup_loader
        def user_lookup_callback(_jwt_header, jwt_data):
            identity = jwt_data["sub"]  # identity 是字符串类型的用户 ID
            return User.query.get(int(identity))  # 将字符串转换为整数后查询用户
    
    return app