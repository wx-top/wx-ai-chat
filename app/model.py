from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Model, User
from common.result import Result

bp = Blueprint('model', __name__)

@bp.route('/models', methods=['GET'])
@jwt_required()
def get_models():
    try:
        models = Model.query.filter_by(is_active=True).all()
        return Result.success(data=[{
            'id': model.id,
            'name': model.name,
            'description': model.description
        } for model in models]).to_json()
    except Exception as e:
        return Result.error(message=str(e)).to_json()

@bp.route('/models', methods=['POST'])
@jwt_required()
def create_model():
    try:
        data = request.json
        if not data or 'name' not in data:
            return Result.bad_request(message="缺少必要参数").to_json()
            
        model = Model(
            name=data['name'],
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        db.session.add(model)
        db.session.commit()
        return Result.success(data={
            'id': model.id,
            'name': model.name,
            'description': model.description
        }).to_json()
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e)).to_json()

@bp.route('/models/<int:model_id>', methods=['PUT'])
@jwt_required()
def update_model(model_id):
    try:
        # user_id = get_jwt_identity()  # 获取字符串类型的用户 ID
        # user = User.query.get_or_404(int(user_id))  # 将字符串转换为整数后查询用户
        model = Model.query.get_or_404(model_id)
        data = request.json
        
        if not data:
            return Result.bad_request(message="缺少更新数据").to_json()
        
        if 'name' in data:
            model.name = data['name']
        if 'description' in data:
            model.description = data['description']
        if 'is_active' in data:
            model.is_active = data['is_active']
        
        db.session.commit()
        return Result.success(data={
            'id': model.id,
            'name': model.name,
            'description': model.description
        }).to_json()
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e)).to_json() 