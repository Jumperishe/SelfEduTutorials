from email import message
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Не коректний E-mail")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=6, max=30, message="Введіть пароль від 6 до 30 символів")])
    remember = BooleanField("Запам'ятати", default=False)
    submit = SubmitField("Увіти")

class RegisterForm(FlaskForm):
    name = StringField("Ім'я: ", validators=[Length(min=4, max=100, message="Ім'я від 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Не коректний E-mail")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=6, max=30, message="Введіть пароль від 6 до 30 символів")])
    psw2 = PasswordField("Повтор пароля:", validators=[DataRequired(), EqualTo('psw', message="Паролі не збігаються")])
    submit = SubmitField("Реєстрація")
