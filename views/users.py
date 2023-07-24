from flask import request, jsonify
from flask_restx import Resource, Namespace

from dao.model.users import UserSchema
from implemented import user_service

user_ns = Namespace('user')
auth_ns = Namespace('auth')
join_ns = Namespace('join')


@user_ns.route('/')  # Получение пользователей
class UserView(Resource):
    def get(self):
        return user_service.get_all()


@user_ns.route('/<int:uid>')
class UserView(Resource):
    def get(self, uid):
        return user_service.get_one(uid)


@auth_ns.route('/')  # Для получения токенов
class UserView(Resource):
    def post(self):
        req_json = request.json
        return user_service.check_user(req_json)

    def put(self):
        req_json = request.json
        tokens = req_json.get("refresh_token")
        return user_service.approve_refresh_token(tokens)


@join_ns.route('/')  # Для добавления пользователей
class UserView(Resource):
    def post(self):
        req_json = request.json
        result = user_service.create(req_json)
        response = jsonify()
        response.status_code = 201
        response.headers['location'] = f'/join/{result.id}'
        return response


# @auth_ns.route('/')
# class UserView(Resource):
#     def put(self):
#         res = user_service.get_all()
#         # #res = DirectorSchema(many=True).dump(rs)
#         return res, 200


@user_ns.route('/')
class UserView(Resource):
    def delete(self):
        res = user_service.get_all()
        return res, 200
