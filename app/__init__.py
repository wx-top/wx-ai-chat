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
        r"/api/*": {
            "origins": "*",  # 允许所有域名访问
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })
    
    # 创建数据库（如果不存在）
    with app.app_context():
        # 从配置中获取数据库连接信息
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        # 解析数据库连接信息
        db_name = db_url.split('/')[-1]
        
        # 解析连接字符串 mysql+pymysql://user:password@host:port/database
        url_parts = db_url.replace('mysql+pymysql://', '').split('@')
        user_pass = url_parts[0].split(':')
        host_port_db = url_parts[1].split('/')
        host_port = host_port_db[0].split(':')
        
        # 创建数据库连接
        conn = pymysql.connect(
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 3306,
            user=user_pass[0],
            password=user_pass[1],
            charset='utf8mb4'
        )
        
        # 创建数据库
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        
        conn.close()
    
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from app.chat import bp as chat_bp
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    from app.model import bp as model_bp
    app.register_blueprint(model_bp, url_prefix='/api/model')
    
    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    from app.repository import bp as repository_bp
    app.register_blueprint(repository_bp, url_prefix='/api/repository')
    
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