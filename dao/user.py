from dao.model.users import User


class UserDAO:
    def __init__(self, session):
        self.session = session

    def get_one_username(self, username):
        try:
            res = self.session.query(User).filter(User.username == username).first()
        except Exception as e:
            return f"Ошибка {e}", 500
        if not res:
            return 404

        return res

    def get_all(self):
        try:
            res = self.session.query(User).all()
        except Exception as e:
            return f"Ошибка {e}", 500
        return res

    def get_one(self, uid):
        try:
            res = self.session.query(User).get(uid)
        except Exception as e:
            return f"Ошибка {e}", 500
        return res

    def create(self, new_user):
        user_inst = User(**new_user)
        try:
            self.session.add(user_inst)
        except Exception as e:
            self.session.rollback()
            print(e)
            return 500
        self.session.commit()
        return user_inst

    def delete(self, rid):
        user = self.get_one(rid)
        self.session.delete(user)
        self.session.commit()

    def update(self, user_d):
        user = self.get_one(user_d.get("id"))
        user.title = user_d.get("title")
        user.description = user_d.get("description")
        user.trailer = user_d.get("trailer")
        user.year = user_d.get("year")
        user.rating = user_d.get("rating")
        user.genre_id = user_d.get("genre_id")
        user.director_id = user_d.get("director_id")

        self.session.add(user)
        self.session.commit()
