# 模型管理 API 文档

## 1. 获取模型列表

### 请求
- **URL**: `/api/model/models`
- **方法**: `GET`
- **Authorization**: `Bearer {access_token}`

### 响应
#### 成功响应 (200)
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "id": 1,
            "name": "GPT-3.5",
            "description": "GPT-3.5 Turbo 模型"
        },
        {
            "id": 2,
            "name": "GPT-4",
            "description": "GPT-4 模型"
        }
    ]
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

## 2. 创建模型

### 请求
- **URL**: `/api/model/models`
- **方法**: `POST`
- **Authorization**: `Bearer {access_token}`
- **Content-Type**: `application/json`

#### 请求参数
```json
{
    "name": "模型名称",
    "description": "模型描述",
    "is_active": true
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
        "name": "模型名称",
        "description": "模型描述"
    }
}
```

#### 错误响应
- 400 Bad Request
```json
{
    "code": 400,
    "message": "缺少必要参数"
}
```
- 401 Unauthorized
```json
{
    "code": 401,
    "message": "未授权"
}
```

## 3. 更新模型

### 请求
- **URL**: `/api/model/models/{model_id}`
- **方法**: `PUT`
- **Authorization**: `Bearer {access_token}`
- **Content-Type**: `application/json`

#### 请求参数
```json
{
    "name": "新模型名称",
    "description": "新模型描述",
    "is_active": false
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
        "name": "新模型名称",
        "description": "新模型描述"
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
    "message": "模型不存在"
}
```

## 使用示例

### 1. 获取模型列表
```javascript
const getModels = async () => {
    const response = await fetchWithAuth('/api/model/models');
    const data = await response.json();
    if (data.code === 200) {
        console.log(data.data);
    }
};
```

### 2. 创建模型
```javascript
const createModel = async (name, description, isActive = true) => {
    const response = await fetchWithAuth('/api/model/models', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, description, is_active: isActive })
    });
    const data = await response.json();
    if (data.code === 200) {
        console.log(data.data);
    }
};
```

### 3. 更新模型
```javascript
const updateModel = async (modelId, updates) => {
    const response = await fetchWithAuth(`/api/model/models/${modelId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
    });
    const data = await response.json();
    if (data.code === 200) {
        console.log(data.data);
    }
};
```

## 注意事项

1. 所有接口都需要认证
2. 创建模型时必须提供名称
3. 更新模型时可以只更新部分字段
4. 模型名称必须唯一
5. 默认情况下，新创建的模型是激活状态 