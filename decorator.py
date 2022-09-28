import jwt
from flask import request
from flask_restx import abort

from constans import secret, algo


def admin_required(func):  # Для проверки прав администратора
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            abort(401)
        data = request.headers['Authorization']
        token = data.split("Bearer ")[-1]
        role = None
        try:
            user = jwt.decode(token, secret, algorithms=[algo])
            role = user.get('role', 'user')

        except Exception as e:
            print("JWT Decode Exсeption", e)
            abort(401)

        if role != 'admin':
            abort(403)
        return func(*args, **kwargs)

    return wrapper


def auth_required(func):  # Для проверки токена
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            abort(401)
        data = request.headers['Authorization']
        token = data.split("Bearer ")[-1]
        try:
            jwt.decode(token, secret, algorithms=[algo])
        except Exception as e:
            print("JWT Decode Exсeption", e)
            abort(401)
        return func(*args, **kwargs)

    return wrapper
