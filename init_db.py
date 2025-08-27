import time
import sys
from sqlalchemy.exc import OperationalError
from app import create_app, db
from app.models import Model

def wait_for_db(app, max_retries=30, delay=2):
    """等待数据库连接就绪"""
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # 尝试执行简单的数据库查询
                db.engine.execute('SELECT 1')
                print(f"数据库连接成功 (尝试 {attempt + 1}/{max_retries})")
                return True
        except OperationalError as e:
            print(f"数据库连接失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                print(f"等待 {delay} 秒后重试...")
                time.sleep(delay)
            else:
                print("数据库连接超时，退出")
                return False
        except Exception as e:
            print(f"未知错误: {str(e)}")
            return False
    return False

def init_db():
    app = create_app()
    
    # 等待数据库就绪
    if not wait_for_db(app):
        print("无法连接到数据库，初始化失败")
        sys.exit(1)
    
    with app.app_context():
        # 创建所有表（如果不存在）
        db.create_all()
        print("数据库表初始化完成")
        
        # 检查是否已存在默认模型
        existing_model = Model.query.filter_by(name='/data/qwen_cyz/qwen_12_add/').first()
        if not existing_model:
            # 添加默认模型
            default_model = Model(
                name='/data/qwen_cyz/qwen_12_add/',
                description='采育震助手',
                is_active=1
            )
            db.session.add(default_model)
            db.session.commit()
            print("默认模型添加完成")
        else:
            print("默认模型已存在，跳过添加")

if __name__ == '__main__':
    init_db()
    print("数据库初始化完成")