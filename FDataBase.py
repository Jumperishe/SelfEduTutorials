from fileinput import filename
from msilib.schema import Binary
import time
import sqlite3
import math
import re

from flask import flash, url_for

class FDataBase:
    def __init__(self, db):
        self. __db = db
        self. __cur = db.cursor()
    
    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: 
                return res
        except:
            print("Error while reading BD")
        return[]
    
    def addPosts(self, title, text):
        try:
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?)", (title, text, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Post add error" + str(e))
            return False
        return True
    
    def getPost(self, postId):
        try:
            self.__cur.execute(f"SELECT title, text FROM posts WHERE id = {postId} LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Error while get post from DB" +str(e))

        return(False, False)
    
    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Get post error from DB" +str(e))
        return[]
    
    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as count FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Користувач з таким E-mail вже існує")
                return False
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка додавання користувача до бази даних" + str(e))
            return False
        
        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Користувач не знайден")
                return False
            return res
        except sqlite3.Error as e:
            print("Помилка отримання даних з БД" +str(e))
        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Користувача не знайдено")
                return False
            
            return res
        except sqlite3.Error as e:
            print("Помилка отримання даних з БД"+str(e))

        return False
    
    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        
        try:
            binary =sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Помилка оновлення аватара у БД" +str(e))
            return False
        return True
        




