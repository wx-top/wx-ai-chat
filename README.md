# wx-ai-chat

基于微信小程序的 AI 聊天应用

## 项目结构

- `python/`: 后端服务，使用 Flask 框架
- `uniapp/`: 前端应用，使用 UniApp 框架

## 技术栈

### 后端
- Python 3.x
- Flask
- SQLAlchemy
- OpenAI API

### 前端
- UniApp
- Vue.js
- 微信小程序

## 开发环境设置

### 后端
1. 创建虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并设置必要的环境变量

### 前端
1. 安装依赖：
```bash
npm install
```

2. 运行开发服务器：
```bash
npm run dev:mp-weixin
```

## 许可证

MIT 