# 聊天接口文档

## 1. 获取会话列表

### 请求
- 方法：GET
- 路径：/api/chat/chats
- 认证：需要 JWT Token

### 响应
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "id": 1,
            "title": "新会话",
            "model_id": 1,
            "created_at": "2024-01-01T00:00:00"
        }
    ]
}
```

## 2. 创建会话

### 请求
- 方法：POST
- 路径：/api/chat/chats
- 认证：需要 JWT Token
- 请求体：
```json
{
    "title": "新会话",
    "model_id": 1
}
```

### 响应
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "title": "新会话",
        "model_id": 1,
        "created_at": "2024-01-01T00:00:00"
    }
}
```

## 3. 获取消息列表

### 请求
- 方法：GET
- 路径：/api/chat/chats/{chat_id}/messages
- 认证：需要 JWT Token

### 响应
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "id": 1,
            "role": "user",
            "content": "你好",
            "created_at": "2024-01-01T00:00:00"
        },
        {
            "id": 2,
            "role": "assistant",
            "content": "你好！有什么我可以帮你的吗？",
            "created_at": "2024-01-01T00:00:01"
        }
    ]
}
```

## 4. 发送消息

### 请求
- 方法：POST
- 路径：/api/chat/chats/{chat_id}/messages
- 认证：需要 JWT Token
- 请求体：
```json
{
    "content": "你好",
    "model_id": 1
}
```

### 响应
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 2,
        "role": "assistant",
        "content": "你好！有什么我可以帮你的吗？",
        "created_at": "2024-01-01T00:00:01"
    }
}
```

### 示例
```javascript
// 发送请求
const response = await fetch('/api/chat/chats/1/messages', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        content: '你好',
        model_id: 1
    })
});

const result = await response.json();
if (result.code === 200) {
    // 处理AI回复
    console.log(result.data.content);
} else {
    // 处理错误
    console.error(result.message);
}
```

## 注意事项
1. 所有接口都需要 JWT Token 认证
2. 创建会话和发送消息时需要指定 model_id
3. 消息内容需要符合模型的要求，否则可能会返回错误 