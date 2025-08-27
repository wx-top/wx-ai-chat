import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_URL = os.getenv('OPENAI_API_URL')
    MODEL_PROVIDER = os.getenv('MODEL_PROVIDER', 'openai')
    MODULE_PROMPT = os.getenv('MODULE_PROMPT')
    EMBEDDINGS_URL = os.getenv('EMBEDDINGS_URL')
    EMBEDDINGS_MODEL = os.getenv('EMBEDDINGS_MODEL')
    # LangSmith配置
    LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY', '')
    LANGSMITH_TRACING = os.getenv('LANGSMITH_TRACING', 'true')
    # Wechat配置
    WECHAT_APPID = os.getenv('WECHAT_APPID')
    WECHAT_SECRET = os.getenv('WECHAT_SECRET')
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
