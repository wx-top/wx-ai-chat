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

if __name__ == '__main__':
    init_db()
    print("数据库初始化完成") 