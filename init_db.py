from app import create_app, db
from app.models import Model, User, Chat, Message

def init_db():
    app = create_app()
    with app.app_context():
        # 创建所有表（如果不存在）
        db.create_all()
        print("数据库表初始化完成")

if __name__ == '__main__':
    init_db()
    print("数据库初始化完成")