from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from app import db
from app.models import Repository, RepositoryFile
from common.result import Result
from app.services.chat_service import ChatService

bp = Blueprint('repository', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    'txt': 1,  # 文本文件
    'pdf': 2,  # PDF文件
    'doc': 3,  # Word文件
    'docx': 3  # Word文件
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return ALLOWED_EXTENSIONS.get(ext, 4)  # 默认为其他类型

@bp.route('/repositories', methods=['POST'])
@jwt_required()
def create_repository():
    """创建知识库"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        if not data or 'name' not in data:
            return Result.bad_request(message="知识库名称不能为空").to_json()
            
        repository = Repository(
            name=data['name'],
            remark=data.get('remark', '')
        )
        db.session.add(repository)
        db.session.commit()
        
        return Result.success(data={
            'id': repository.id,
            'name': repository.name,
            'remark': repository.remark,
            'created_at': repository.created_at.isoformat()
        }).to_json()
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e)).to_json()

@bp.route('/repositories/<int:repository_id>/files', methods=['POST'])
@jwt_required()
def upload_file(repository_id):
    """上传知识库文件"""
    try:
        # 检查知识库是否存在
        repository = Repository.query.get_or_404(repository_id)

        if not repository:
            return Result.bad_request(message="知识库不存在").to_json()
        
        # 获取文件名参数
        name = request.args.get('name')
        if not name:
            return Result.bad_request(message="文件名不能为空").to_json()
        
        if 'file' not in request.files:
            return Result.bad_request(message="未上传文件").to_json()
        
        file = request.files['file']
        if file.filename == '':
            return Result.bad_request(message="未选择文件").to_json()
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return Result.bad_request(message="不支持的文件类型").to_json()
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        filename = f"{repository_id}_{filename}"  # 添加知识库ID前缀避免文件名冲突
        
        # 确保上传目录存在
        upload_dir = os.path.join(current_app.static_folder, 'repository_files')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取文件类型
        file_type = get_file_type(filename)

        cs = ChatService(repository_id=repository_id)
        file_id = cs.load_documents(file_path, file_type)

        
        # 保存文件记录到数据库
        repository_file = RepositoryFile(
            repository_id=repository_id,
            file=f"/static/repository_files/{filename}",
            name=name,  # 使用URL参数中的name
            size=file_size,  # 保存文件大小
            file_id=file_id,
            type=file_type
        )
        db.session.add(repository_file)
        db.session.commit()

        return Result.success(data={
            'id': repository_file.id,
            'file': repository_file.file,
            'name': repository_file.name,
            'size': repository_file.size,  # 添加文件大小
            'type': repository_file.type,
            'created_at': repository_file.created_at.isoformat()
        }).to_json()
        
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e)).to_json()

@bp.route('/repositories', methods=['GET'])
@jwt_required()
def get_repositories():
    """获取知识库列表"""
    try:
        repositories = Repository.query.order_by(Repository.created_at.desc()).all()
        return Result.success(data=[{
            'id': repo.id,
            'name': repo.name,
            'remark': repo.remark,
            'created_at': repo.created_at.isoformat()
        } for repo in repositories]).to_json()
    except Exception as e:
        return Result.error(message=str(e)).to_json()

@bp.route('/repositories/<int:repository_id>/files', methods=['GET'])
@jwt_required()
def get_repository_files(repository_id):
    """获取知识库文件列表"""
    try:
        repository = Repository.query.get_or_404(repository_id)
        files = RepositoryFile.query.filter_by(repository_id=repository_id).order_by(RepositoryFile.created_at.desc()).all()
        return Result.success(data=[{
            'id': file.id,
            'file': file.file,
            'name': file.name,
            'size': file.size,  # 添加文件大小
            'type': file.type,
            'created_at': file.created_at.isoformat()
        } for file in files]).to_json()
    except Exception as e:
        return Result.error(message=str(e)).to_json()

@bp.route('/repositories/<int:repository_id>/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(repository_id, file_id):
    """删除知识库文件"""
    try:
        # 检查知识库是否存在
        repository = Repository.query.get_or_404(repository_id)



        if not repository:
            return Result.bad_request(message="知识库不存在").to_json()
        
        # 检查文件是否存在
        file = RepositoryFile.query.filter_by(id=file_id, repository_id=repository_id).first_or_404()
        
        # 删除物理文件
        file_path = os.path.join(current_app.static_folder, file.file.lstrip('/static/'))
        if os.path.exists(file_path):
            os.remove(file_path)

        cs = ChatService(repository_id=repository_id)
        cs.delete_documents(file_id=file_id)
        
        # 删除数据库记录
        db.session.delete(file)
        db.session.commit()
        
        return Result.success().to_json()
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e)).to_json()

@bp.route('/repositories/<int:repository_id>', methods=['DELETE'])
@jwt_required()
def delete_repository(repository_id):
    """删除知识库"""
    try:
        repository = Repository.query.get_or_404(repository_id)
        # 删除文件记录
        RepositoryFile.query.filter_by(repository_id=repository_id).delete()
        
        # 删除知识库
        db.session.delete(repository)
        db.session.commit()
        
        return Result.success().to_json()
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e)).to_json()

@bp.route('/repositories/<int:repository_id>', methods=['PUT'])
@jwt_required()
def update_repository(repository_id):
    """更新知识库"""
    try:
        repository = Repository.query.get_or_404(repository_id)
        data = request.json
        
        if not data:
            return Result.bad_request(message="请求数据不能为空").to_json()
            
        # 更新知识库名称
        if 'name' in data:
            if not data['name']:
                return Result.bad_request(message="知识库名称不能为空").to_json()
            repository.name = data['name']
            
        # 更新备注
        if 'remark' in data:
            repository.remark = data['remark']
            
        db.session.commit()
        
        return Result.success(data={
            'id': repository.id,
            'name': repository.name,
            'remark': repository.remark,
            'created_at': repository.created_at.isoformat()
        }).to_json()
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e)).to_json() 