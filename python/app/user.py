from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from app import db
from app.models import User
from common.result import Result

bp = Blueprint('user', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()  # 获取字符串类型的用户 ID
    user = User.query.get_or_404(int(user_id))  # 将字符串转换为整数后查询用户
    return Result.success(data={
        'id': user.id,
        'nickname': user.nickname,
        'avatar': user.avatar,
        'created_at': user.created_at.isoformat()
    }).to_json()

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()  # 获取字符串类型的用户 ID
    user = User.query.get_or_404(int(user_id))  # 将字符串转换为整数后查询用户
    
    data = request.get_json()
    if not data:
        return Result.bad_request(message="缺少更新数据").to_json()
    
    if 'nickname' in data:
        user.nickname = data['nickname']
    
    db.session.commit()
    return Result.success(data={
        'id': user.id,
        'nickname': user.nickname,
        'avatar': user.avatar,
        'created_at': user.created_at.isoformat()
    }).to_json()

@bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    user_id = get_jwt_identity()  # 获取字符串类型的用户 ID
    user = User.query.get_or_404(int(user_id))  # 将字符串转换为整数后查询用户
    
    if 'file' not in request.files:
        return Result.bad_request(message="未上传文件").to_json()
    
    file = request.files['file']
    if file.filename == '':
        return Result.bad_request(message="未选择文件").to_json()
    
    # 检查文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not file.filename.lower().endswith(tuple(allowed_extensions)):
        return Result.bad_request(message="不支持的文件类型").to_json()
    
    # 生成安全的文件名
    filename = secure_filename(file.filename)
    filename = f"{user_id}_{filename}"  # 添加用户 ID 前缀避免文件名冲突
    
    # 确保上传目录存在
    upload_dir = os.path.join(current_app.static_folder, 'avatars')
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    # 更新用户头像
    user.avatar = f"/static/avatars/{filename}"
    db.session.commit()
    
    return Result.success(data={
        'avatar_url': user.avatar
    }).to_json()
