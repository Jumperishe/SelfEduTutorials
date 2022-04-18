import re
import sqlite3
import os
from flask import Flask, flash, make_response, render_template, request, g, url_for, abort, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from UserLogin import UserLogin
from forms import RegisterForm, LoginForm
from admin.admin import admin

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'ababagalimagagalimagababa'
MAX_CONTENT_LENGHT = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

#---------------------Blueprint registration-----------------------------
app.register_blueprint(admin, url_prefix='/admin')
#------------------------------------------------------------------------

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтеся для перегляду та додавання статей"
login_manager.login_message_category = "success"
dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode = 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

def checkEmailForm(email):    
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email)):
            return True
        else:
            return False

@app.route("/add_post", methods=["POST", "GET"])
@login_required
      
def addPost():
    #if current_user.is_authenticated:
        if request.method == 'POST':
            if len(request.form['name']) > 4 and len(request.form['post']) > 10:
                res = dbase.addPosts(request.form['name'], request.form['post'])
                if not res:
                    flash("Помилка додавання повідомлення", category='error')
                else:
                    flash('Повідомлення додано успішно', category='success')
            else:
                flash('Помилка додавання повідомлення', category='error')
        return render_template('add_post.html', menu = dbase.getMenu(), title = "Додати повідомлення")
    #return redirect(request.args.get("next") or url_for("profile"))

@app.route("/")
def index():
    return render_template('index.html', menu = dbase.getMenu(), posts = dbase.getPostsAnonce())


@app.route("/post/<int:id_post>")
@login_required
def showPost(id_post):
    title, post = dbase.getPost(id_post)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)

@app.route("/login", methods = ["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit(): 
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userLogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userLogin, remember = rm)
            return redirect(request.args.get("next") or url_for("profile"))
        flash("Невірна пара логін пароль", "error")  

    
    return render_template("login.html", menu=dbase.getMenu(), title="Авторизація", form = form)
# --------------------- /register route without WTForm module---------------------------------------- 
# @app.route("/register", methods=["POST", "GET"])
# def register():
#     if request.method == 'POST':
#         if checkEmailForm(request.form['email']):
            
#             if (len(request.form['psw']) < 5 and len(request.form['psw2']) < 5) or request.form['psw'] != request.form['psw2']:              
#                 flash("Паролі не збігаються, або меньше п'яти символів", 'error')
              
#             else:
#                 hash = generate_password_hash(request.form['psw'])
#                 res = dbase.addUser(request.form['name'], request.form['email'], hash)
#                 if res:
#                     flash("Успішна реєстрація", "success")
#                     return redirect(url_for('login'))
#                 else:
#                     flash("Користувач з таким E-mail вже існує", "error")
#         else:
#             flash("Невірні значення поля  E-mail", 'error')
#     return render_template("register.html", menu=dbase.getMenu(), title = "Реєстрація" )
#---------------------------------------------------------------------------------

# --------------------- /register route with WTForm module -------------------------------------------
@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(request.form['psw'])
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash("Реєстрація успішна!", "success")
            return redirect(url_for('login'))
        else:
            flash("Помилка про запису до БД", "error")
    return render_template("register.html", menu = dbase.getMenu(), title="Реєстрація", form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("Ви вийшли з аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title = "Профіль")

@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Помилка оновлення аватара", "error")
                    
                flash("Аватр оновлено", "success")
            except:
                flash("Помилка завантаження аватару", "error")
    return redirect(url_for('profile'))
            



@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

              
              
if __name__ =="__main__":
    app.run(debug=True)

