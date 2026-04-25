from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    position = StringField("Звание", validators=[DataRequired()])
    speciality = StringField("Профессия", validators=[DataRequired()])
    address = StringField("Адрес", validators=[DataRequired()])
    age = IntegerField("Возраст", validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class JobForm(FlaskForm):
    team_leader = IntegerField("team_leader_id", validators=[DataRequired()])
    job = StringField('Описание работы', validators=[DataRequired()])
    work_size = IntegerField("Объем работы", validators=[DataRequired()])
    collaborators = StringField("Кто участвует?", validators=[DataRequired()])
    is_finished = BooleanField("Работа завершена?")
