from flask import Flask, url_for

class UserLogin():
    
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.__user['id'])
    
    def getName(self):
        return self.__user['name'] if self.__user else "Без ім'я"

    def getEmail(self):
        return self.__user['email'] if self.__user else "Без Email"

    def getAvatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не знайдено аватар за змовчуванням" + str(e))
        else: 
            img = self.__user['avatar']
        
        return img

