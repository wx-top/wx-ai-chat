# 认证 API 文档

## 1. 微信登录

### 请求
- **URL**: `/api/auth/login`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
```json
{
    "code": "微信登录code"
}
```

### 响应
#### 成功响应 (200)
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "access_token": "访问令牌",
        "refresh_token": "刷新令牌",
        "user": {
            "id": 1,
            "nickname": "用户昵称",
            "avatar": "用户头像URL"
        }
    }
}
```

#### 错误响应
- 400 Bad Request
```json
{
    "code": 400,
    "message": "缺少code参数"
}
```
- 500 Internal Server Error
```json
{
    "code": 500,
    "message": "错误信息"
}
```

## 2. 刷新令牌

### 请求
- **URL**: `/api/auth/refresh`
- **方法**: `POST`
- **Authorization**: `Bearer {refresh_token}`

### 响应
#### 成功响应 (200)
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "access_token": "新的访问令牌"
    }
}
```

#### 错误响应
- 401 Unauthorized
```json
{
    "code": 401,
    "message": "未授权"
}
```

## 3. 登出

### 请求
- **URL**: `/api/auth/logout`
- **方法**: `POST`
- **Authorization**: `Bearer {access_token}`

### 响应
#### 成功响应 (200)
```json
{
    "code": 200,
    "message": "success"
}
```

## 认证头格式

所有需要认证的 API 请求都需要在请求头中包含 `Authorization` 字段：

```
Authorization: Bearer {access_token}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 500 | 服务器内部错误 |

## 使用示例

### 1. 登录
```javascript
const login = async (code) => {
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code })
    });
    const data = await response.json();
    if (data.code === 200) {
        // 存储令牌
        localStorage.setItem('access_token', data.data.access_token);
        localStorage.setItem('refresh_token', data.data.refresh_token);
    }
};
```

### 2. 刷新令牌
```javascript
const refreshToken = async () => {
    const refresh_token = localStorage.getItem('refresh_token');
    const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${refresh_token}`
        }
    });
    const data = await response.json();
    if (data.code === 200) {
        localStorage.setItem('access_token', data.data.access_token);
    }
};
```

### 3. 登出
```javascript
const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
};
```

### 4. 请求拦截器示例
```javascript
const fetchWithAuth = async (url, options = {}) => {
    const access_token = localStorage.getItem('access_token');
    const response = await fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${access_token}`
        }
    });
    
    // 处理 token 过期
    if (response.status === 401) {
        await refreshToken();
        // 重试原请求
        return fetchWithAuth(url, options);
    }
    
    return response;
};
```

## 注意事项

1. 访问令牌（access_token）有效期为 1 天
2. 刷新令牌（refresh_token）有效期为 30 天
3. 所有需要认证的 API 都需要在请求头中携带 access_token
4. 当 access_token 过期时，使用 refresh_token 获取新的 access_token
5. 登出时只需要在前端删除存储的令牌即可 