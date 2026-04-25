import flask_login
from flask import Flask, render_template, url_for, request, make_response, redirect, jsonify
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user
from data.Forms import LoginForm, RegisterForm
from flask_restful import reqparse, abort, Api, Resource
from data.users import User
from data import users_resources

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/')
def page():
    return render_template('first_page.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()
