from msilib.schema import Error
import sqlite3
from flask import Blueprint, redirect, render_template, url_for, flash, request, session, g

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

menu = [{'url': 'index', 'title': 'Головна'},
        {'url': '.listusers', 'title': 'Користувачі'},
        {'url': '.listposts', 'title': 'Повідомлення'},
        {'url': '.logout', 'title': 'Вийти'}]

db = None
@admin.before_request
def before_request():
    global db
    db = g.get('link_db')


def login_admin():
    session['admin_logged'] = 1

def isLogged():
    return True if session.get('admin_logged') else False   

def logout_admin():
    session.pop('admin_logged', None)

@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))
    
    return render_template('admin/index.html', menu = menu, title="Адмін-панель") 

@admin.route('/login', methods = ['POST', 'GET'])
def login():
    if isLogged():
        return redirect(url_for('.index'))
    if request.method == "POST":
        if request.form['user'] == "admin" and request.form['psw'] == "159263":
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Невірний логін або пароль", "error")
    return render_template('admin/login.html', title = 'Адмін-панель' )

@admin.route('/logout', methods = ["POST","GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))
    logout_admin()
    return redirect(url_for('.login'))

@admin.route('/listposts')
def listposts():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT id, text, title FROM posts ORDER BY time DESC")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Помилка читання статей з БД", str(e))
    return render_template('admin/listposts.html', title='Список повідомлень', menu=menu, list=list)

@admin.route('/listusers')
def listusers():
   
    if not isLogged():
        return redirect(url_for('.login'))
    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT name, email FROM users ORDER BY time DESC")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Помилка читання списку користувачів" + str(e)) 

    return render_template('admin/listusers.html', title = 'Список користувачів', menu=menu, list=list )    

