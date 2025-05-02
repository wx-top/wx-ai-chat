from app import create_app, db
from app.models import Model, User, Chat, Message

def init_db():
    app = create_app()
    with app.app_context():
        # 删除所有表（如果存在）
        db.drop_all()
        
        # 创建所有表
        db.create_all()
        print("已创建数据库表")
        
        # 初始化默认模型
        try:
            default_models = [
                Model(name='GPT-3.5', description='GPT-3.5 Turbo 模型'),
                Model(name='GPT-4', description='GPT-4 模型'),
                Model(name='Claude', description='Claude 模型')
            ]
            db.session.add_all(default_models)
            db.session.commit()
            print("已创建默认模型")
        except Exception as e:
            print(f"初始化默认模型时出错: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_db()
    print("数据库初始化完成") 