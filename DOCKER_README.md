# Docker 部署指南

本项目包含前端（UniApp H5）和后端（Flask）两个服务，可以使用 Docker 进行容器化部署。

## 项目结构

```
wx-ai-chat/
├── Dockerfile              # 后端 Dockerfile
├── docker-compose.yml      # Docker Compose 配置
├── .dockerignore           # Docker 忽略文件
├── requirements.txt        # Python 依赖
├── run.py                 # Flask 应用入口
├── web/
│   ├── Dockerfile         # 前端 Dockerfile
│   ├── nginx.conf         # Nginx 配置
│   ├── .dockerignore      # 前端 Docker 忽略文件
│   └── package.json       # Node.js 依赖
└── ...
```

## 快速开始

### 使用 Docker Compose（推荐）

1. **构建并启动所有服务**：
   ```bash
   docker-compose up --build
   ```

2. **后台运行**：
   ```bash
   docker-compose up -d --build
   ```

3. **停止服务**：
   ```bash
   docker-compose down
   ```

### 单独构建镜像

#### 后端镜像

```bash
# 构建后端镜像
docker build -t wx-ai-chat-backend .

# 运行后端容器
docker run -d -p 5000:5000 --name backend wx-ai-chat-backend
```

#### 前端镜像

```bash
# 进入前端目录
cd web

# 构建前端镜像
docker build -t wx-ai-chat-frontend .

# 运行前端容器
docker run -d -p 80:80 --name frontend wx-ai-chat-frontend
```

## 服务访问

- **前端应用**: http://localhost
- **后端API**: http://localhost:5000
- **健康检查**: http://localhost/health

## 环境配置

### 后端环境变量

可以通过环境变量或 `.env` 文件配置后端服务：

```bash
# Flask 环境
FLASK_ENV=production
PYTHONPATH=/app

# 数据库配置（如果使用外部数据库）
DATABASE_URL=mysql://user:password@host:port/database
```

### 前端环境变量

前端配置通过 `web/.env` 文件管理：

```bash
VITE_APP_NAME=采育镇助手
VITE_API_BASE_URL=https://api.wenxin.icu
VITE_DEBUG=false
```

## 数据持久化

### 后端数据

Docker Compose 配置中已包含数据卷映射：

- `./chroma_db:/app/chroma_db` - 向量数据库
- `./app/static:/app/app/static` - 静态文件

### 数据库（可选）

如需使用独立的 MySQL 容器，可取消注释 `docker-compose.yml` 中的 MySQL 服务配置。

## 生产环境部署

### 1. 修改配置

- 更新 `web/.env` 中的 API 地址
- 配置生产环境的数据库连接
- 设置适当的环境变量

### 2. 使用反向代理

建议在生产环境中使用 Nginx 或 Traefik 作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:80;
    }
    
    location /api/ {
        proxy_pass http://localhost:5000/;
    }
}
```

### 3. HTTPS 配置

使用 Let's Encrypt 或其他 SSL 证书提供商配置 HTTPS。

## 故障排除

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 实时查看日志
docker-compose logs -f
```

### 进入容器调试

```bash
# 进入后端容器
docker exec -it wx-ai-chat-backend bash

# 进入前端容器
docker exec -it wx-ai-chat-frontend sh
```

### 重新构建

```bash
# 强制重新构建
docker-compose build --no-cache

# 清理未使用的镜像
docker system prune -a
```

## 注意事项

1. **端口冲突**: 确保 80 和 5000 端口未被占用
2. **内存要求**: 建议至少 2GB 可用内存
3. **磁盘空间**: 确保有足够空间存储镜像和数据
4. **网络配置**: 如使用外部数据库，确保网络连通性

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up --build -d

# 清理旧镜像
docker image prune -f
```