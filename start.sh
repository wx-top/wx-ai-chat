#!/bin/bash

# 数据库初始化
echo "正在初始化数据库..."
python init_db.py

if [ $? -eq 0 ]; then
    echo "数据库初始化成功"
else
    echo "数据库初始化失败"
    exit 1
fi

# 启动gunicorn服务
echo "正在启动应用服务..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app