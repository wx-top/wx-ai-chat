from flask import Blueprint, request, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import requests
from app import db
from app.models import User
from common.result import Result

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def wechat_login():
    code = request.json.get('code')
    if not code:
        return Result.bad_request(message="缺少code参数").to_json()
    
    try:
        # 获取微信用户openid
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": current_app.config["WECHAT_APPID"],
            "secret": current_app.config["WECHAT_SECRET"],
            "js_code": code,
            "grant_type": "authorization_code"
        }
        response = requests.get(url, params=params)
        data = response.json()
        errcode = data.get('errcode')

        if errcode:
            print(data.get('errmsg'))
            return Result.error(message="登录失败").to_json()
            
        openid = data['openid']
        # 查找或创建用户
        user = User.query.filter_by(openid=openid).first()
        if not user:
            user = User(openid=openid)
            db.session.add(user)
            db.session.commit()
            # 重新获取用户以确保有ID
            user = User.query.filter_by(openid=openid).first()
        
        # 创建访问令牌和刷新令牌，确保identity是字符串
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        
        return Result.success(data={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'nickname': user.nickname,
                'avatar': user.avatar
            }
        }).to_json()
        
    except Exception as e:
        print(f"登录错误: {str(e)}")
        return Result.error(message=str(e)).to_json()

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return Result.success(data={'access_token': access_token}).to_json()

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # 在前端删除 token 即可
    return Result.success().to_json() 