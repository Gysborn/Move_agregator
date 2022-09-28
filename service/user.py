import base64
import calendar
import datetime
import hashlib
import hmac

import jwt

from constans import PWD_HASH_SALT, PWD_HASH_ITERATIONS, secret, algo
from dao.model.users import UserSchema
from dao.user import UserDAO




class UserService:
    def __init__(self, dao: UserDAO):
        self.dao = dao

    def get_by_username(self, username):
        return self.dao.get_one_username(username)

    def get_all(self):
        user = self.dao.get_all()
        if not user:
            return "Пользователь не найден", 404
        if user == 500:
            return "Непредвиденная ошибка", 500
        res = UserSchema(many=True).dump(user)
        return res

    def get_one(self, uid):
        user = self.dao.get_one(uid)
        if not user:
            return "Пользователь не найден", 404
        if user == 500:
            return "Непредвиденная ошибка", 500
        res = UserSchema().dump(user)
        return res

    def create(self, new_user):
        username = new_user['username']
        password = new_user['password']
        if None in [password, username]:
            return False
        new_user['password'] = self.get_hash(new_user.get('password'))  # Зашифровали пароль
        result = self.dao.create(new_user)
        if 500 == result:
            return "Непредвиденная ошибка", 500
        return result

    def update(self, movie_d):
        self.dao.update(movie_d)
        return self.dao

    def delete(self, rid):
        self.dao.delete(rid)

    def get_hash(self, password):  # Кодируем пароль
        hash_digest = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),  # Convert the password to bytes
            PWD_HASH_SALT,
            PWD_HASH_ITERATIONS
        )
        return base64.b64encode(hash_digest)

    def compair_pass(self, pass_hash, clear_pass) -> bool:
        hash_digest = self.get_hash(clear_pass)
        return hmac.compare_digest(pass_hash, hash_digest)

    def approve_refresh_token(self, refresh_token):
        try:
            data = jwt.decode(jwt=refresh_token, key=secret, algorithms=[algo])
        except Exception as e:
            return f"Непредвиденная ошибка {e}", 500
        return self.check_user(data, True)

    def check_user(self, user_json: dict, is_refresh=False):
        username = user_json.get('username')
        password = user_json.get('password')
        if None in [username, password]:
            return '', 400
        user = self.dao.get_one_username(username)
        if not user:
            return "Непредвиденная ошибка", 500
        if user == 404:
            return "Пользователь не найден", 404
        if not is_refresh:
            pass_hash = getattr(user, 'password')
            user_json["role"] = getattr(user, 'role', 'user')
            if not self.compair_pass(pass_hash, password):
                return 'Неверный пароль или логин', 403

        return self.generate_jwt(user_json)

    def generate_jwt(self, user_obj):
        # Создаем access_token на 30 мин
        min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        user_obj["exp"] = calendar.timegm(min30.timetuple())
        access_token = jwt.encode(user_obj, secret, algorithm=algo)

        # Создаем refresh_token 130 дней
        days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        user_obj["exp"] = calendar.timegm(days130.timetuple())
        refresh_token = jwt.encode(user_obj, secret, algorithm=algo)
        return {"access_token": access_token, "refresh_token": refresh_token}
