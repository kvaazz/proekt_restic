from flask import Flask
from data import db_session
from data.Forms import LoginForm, RegisterForm
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user
from flask import Flask, render_template, url_for, request, make_response, redirect, jsonify


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


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