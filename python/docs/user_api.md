# 用户管理 API 文档

## 1. 获取用户信息

### 请求
- **URL**: `/api/user/profile`
- **方法**: `GET`
- **Authorization**: `Bearer {access_token}`

### 响应
#### 成功响应 (200)
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "nickname": "用户昵称",
        "avatar": "头像URL",
        "created_at": "2024-01-01T00:00:00"
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
- 404 Not Found
```json
{
    "code": 404,
    "message": "用户不存在"
}
```

## 2. 更新用户信息

### 请求
- **URL**: `/api/user/profile`
- **方法**: `PUT`
- **Authorization**: `Bearer {access_token}`
- **Content-Type**: `application/json`

#### 请求参数
```json
{
    "nickname": "新昵称"
}
```

### 响应
#### 成功响应 (200)
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "nickname": "新昵称",
        "avatar": "头像URL",
        "created_at": "2024-01-01T00:00:00"
    }
}
```

#### 错误响应
- 400 Bad Request
```json
{
    "code": 400,
    "message": "缺少更新数据"
}
```
- 401 Unauthorized
```json
{
    "code": 401,
    "message": "未授权"
}
```
- 404 Not Found
```json
{
    "code": 404,
    "message": "用户不存在"
}
```

## 3. 上传头像

### 请求
- **URL**: `/api/user/avatar`
- **方法**: `POST`
- **Authorization**: `Bearer {access_token}`
- **Content-Type**: `multipart/form-data`

#### 请求参数
| 参数名 | 类型 | 说明 |
|--------|------|------|
| file | File | 图片文件，支持 png、jpg、jpeg、gif 格式 |

### 响应
#### 成功响应 (200)
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "avatar": "/static/avatars/1_avatar.jpg"
    }
}
```

#### 错误响应
- 400 Bad Request
```json
{
    "code": 400,
    "message": "没有文件/没有选择文件/不支持的文件类型"
}
```
- 401 Unauthorized
```json
{
    "code": 401,
    "message": "未授权"
}
```
- 404 Not Found
```json
{
    "code": 404,
    "message": "用户不存在"
}
```

## 使用示例

### 1. 获取用户信息
```javascript
const getProfile = async () => {
    const response = await fetchWithAuth('/api/user/profile');
    const data = await response.json();
    if (data.code === 200) {
        console.log(data.data);
    }
};
```

### 2. 更新用户信息
```javascript
const updateProfile = async (nickname) => {
    const response = await fetchWithAuth('/api/user/profile', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nickname })
    });
    const data = await response.json();
    if (data.code === 200) {
        console.log(data.data);
    }
};
```

### 3. 上传头像
```javascript
const uploadAvatar = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetchWithAuth('/api/user/avatar', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    if (data.code === 200) {
        console.log(data.data.avatar);
    }
};
```

## 注意事项

1. 所有接口都需要认证
2. 头像上传支持的文件格式：png、jpg、jpeg、gif
3. 头像文件会保存在服务器的 static/avatars 目录下
4. 头像文件名格式为：{user_id}_{original_filename}
5. 头像URL格式为：/static/avatars/{filename} 