from app import create_app, db
from app.models import Model

def init_db():
    app = create_app()
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