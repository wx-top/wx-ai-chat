from typing import Any, Dict, Optional
from flask import jsonify

class Result:
    def __init__(self, code: int = 200, message: str = "success", data: Any = None):
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }

    def to_json(self):
        return jsonify(self.to_dict())

    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> 'Result':
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, message: str = "error", code: int = 500, data: Any = None) -> 'Result':
        return cls(code=code, message=message, data=data)

    @classmethod
    def not_found(cls, message: str = "资源不存在") -> 'Result':
        return cls(code=404, message=message)

    @classmethod
    def unauthorized(cls, message: str = "未授权") -> 'Result':
        return cls(code=401, message=message)

    @classmethod
    def forbidden(cls, message: str = "禁止访问") -> 'Result':
        return cls(code=403, message=message)

    @classmethod
    def bad_request(cls, message: str = "请求参数错误") -> 'Result':
        return cls(code=400, message=message)

