from flask import Blueprint, request, current_app, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from langchain_core.messages import AIMessage
import time

from app import db
from app.models import Chat, Message, Model, User
from app.services.chat_service import ChatService
from common.result import Result
import json

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


@bp.route('/chats/<int:chat_id>/messages/stream', methods=['POST'])
@jwt_required()
def send_message_stream(chat_id):
    """流式聊天接口"""
    try:
        print(f"开始处理流式聊天请求，chat_id: {chat_id}")
        user_id = get_jwt_identity()
        user = User.query.get_or_404(int(user_id))
        chat = Chat.query.filter_by(id=chat_id, user_id=user.id).first_or_404()
        
        data = request.json
        content = data.get('content')
        model_id = data.get('model_id')
        repository_id = data.get('repository_id') or None
        
        print(f"请求参数: content={content}, model_id={model_id}, repository_id={repository_id}")
        
        if not content:
            return Result.bad_request(message="消息内容不能为空").to_json()
        if not model_id:
            return Result.bad_request(message="请选择模型").to_json()
            
        # 查询模型信息
        model = Model.query.get_or_404(model_id)
        print(f"使用模型: {model.name}")
        
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
        
        # 使用 LangChain 处理聊天，传入知识库ID
        chat_service = ChatService(model.name, repository_id)
        print("ChatService 创建成功，开始流式处理...")
        stream_response = chat_service.chat_stream(chat_id, content)
        print("开始生成流式响应...")
        
        def generate():
            full_content = ""  # 用于收集完整的AI回复
            try:
                for chunk in stream_response:
                    message = chunk[0]
                    if isinstance(message, AIMessage):  # Filter to just model responses
                        print(message.content, end="")
                        full_content += message.content  # 累积内容
                        yield message.content
            except Exception as e:
                error_type = type(e).__name__  # 获取异常类型（如 "ValueError"）
                error_message = ""
                print(f"请求异常：{str(e)}")
                if error_type == "BadRequestError":
                    error_message = "请求异常，请稍后重试"
                yield error_message
            finally:
                # 流式传输完成后，保存AI回复到数据库
                if full_content and not full_content.startswith("错误:"):
                    try:
                        # 保存AI消息到数据库
                        ai_message = Message(chat_id=chat_id, role='assistant', content=full_content)
                        db.session.add(ai_message)
                        db.session.commit()
                        print(f"AI回复已保存到数据库，内容长度: {len(full_content)}")
                    except Exception as save_error:
                        print(f"保存AI回复到数据库时出错: {str(save_error)}")
                        db.session.rollback()
                
        return Response(stream_with_context(generate()), content_type='text/plain')
    except Exception as e:
        print(f"流式聊天接口错误: {str(e)}")
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