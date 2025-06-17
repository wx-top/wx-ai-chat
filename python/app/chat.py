from flask import Blueprint, request, current_app, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Chat, Message, Model, User
from app.services.chat_service import ChatService
from common.result import Result

bp = Blueprint('chat', __name__)

@bp.route('/chats', methods=['GET'])
@jwt_required()
def get_chats():
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(int(user_id))
        chats = Chat.query.filter_by(user_id=user.id).order_by(Chat.created_at.desc()).all()
        return Result.success(data=[{
            'id': chat.id,
            'title': chat.title,
            'created_at': chat.created_at.isoformat()
        } for chat in chats]).to_json()
    except Exception as e:
        return Result.error(message=str(e)).to_json()

@bp.route('/chats', methods=['POST'])
@jwt_required()
def create_chat():
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(int(user_id))
        data = request.json
        title = data.get('title', '新会话')
        
        chat = Chat(user_id=user.id, title=title)
        db.session.add(chat)
        db.session.commit()
        return Result.success(data={
            'id': chat.id,
            'title': chat.title,
            'created_at': chat.created_at.isoformat()
        }).to_json()
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e)).to_json()

@bp.route('/chats/<int:chat_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(chat_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(int(user_id))
        chat = Chat.query.filter_by(id=chat_id, user_id=user.id).first_or_404()
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at.asc()).all()
        return Result.success(data=[{
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'created_at': msg.created_at.isoformat()
        } for msg in messages]).to_json()
    except Exception as e:
        return Result.error(message=str(e)).to_json()

@bp.route('/chats/<int:chat_id>/messages', methods=['POST'])
@jwt_required()
def send_message(chat_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(int(user_id))
        chat = Chat.query.filter_by(id=chat_id, user_id=user.id).first_or_404()
        
        data = request.json
        content = data.get('content')
        model_id = data.get('model_id')
        repository_id = data.get('repository_id') or None
        print(f"{model_id}:{repository_id}")
        
        if not content:
            return Result.bad_request(message="消息内容不能为空").to_json()
        if not model_id:
            return Result.bad_request(message="请选择模型").to_json()
            
        # 查询模型信息
        model = Model.query.get_or_404(model_id)
        
        # 检查是否是第一条消息
        is_first_message = Message.query.filter_by(chat_id=chat_id).count() == 0
        
        # 保存用户消息
        user_message = Message(chat_id=chat_id, role='user', content=content)
        db.session.add(user_message)
        db.session.commit()
        
        # 如果是第一条消息，使用消息内容的前8个字作为标题
        if is_first_message:
            chat.title = content[:8] + '...' if len(content) > 8 else content
            db.session.commit()
        
        # 获取历史消息
        # history_messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at.asc()).all()
        # messages = [{'role': msg.role, 'content': msg.content} for msg in history_messages]
        
        # 使用 LangChain 处理聊天，传入知识库ID
        print(f'模型名字 {model.name}' )
        chat_service = ChatService(model.name, repository_id)
        ai_content = chat_service.chat(chat_id, content)

        
        # 保存AI消息
        ai_message = Message(chat_id=chat_id, role='assistant', content=ai_content)
        db.session.add(ai_message)
        db.session.commit()
        
        return Result.success(data={
            'id': ai_message.id,
            'role': ai_message.role,
            'content': ai_message.content,
            'created_at': ai_message.created_at.isoformat()
        }).to_json()
        
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e)).to_json()

@bp.route('/chats/<int:chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(chat_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(int(user_id))
        chat = Chat.query.filter_by(id=chat_id, user_id=user.id).first_or_404()
        
        # 删除会话相关的所有消息
        Message.query.filter_by(chat_id=chat_id).delete()
        # 删除会话
        db.session.delete(chat)
        db.session.commit()
        
        return Result.success().to_json()
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e)).to_json() 