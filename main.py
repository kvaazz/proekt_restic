from flask_login import current_user
from flask import Flask, render_template, url_for, request, make_response, redirect, jsonify
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user
from data.Forms import LoginForm, RegisterForm
from flask_restful import reqparse, abort, Api, Resource
from data.users import User
from data import users_resources
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/')
def page():
    return render_template('first_page.html')


@app.route('/location', methods=['GET', 'POST'])
def location():
    api_server = 'https://static-maps.yandex.ru/v1?'
    toponym_longitude = 31.253898
    toponym_lattitude = 58.525216
    API_KEY = "c7e6930c-2621-45c2-9bf7-3b85675e054c"

    params = {
        "apikey": API_KEY,
        "ll": ",".join([str(toponym_longitude), str(toponym_lattitude)]),
        "pt": ",".join([str(toponym_longitude), str(toponym_lattitude), str('pm2dbm')]),
        'z': '13'
    }

    response = requests.get(api_server, params=params)

    if not response:
        print("Ошибка выполнения запроса:")
        print(response)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    map_file = "static/upload/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)

    if request.method == 'POST':
        geocode = request.form.get('address')
        if not geocode:
            print('Пожалуйста, введите адрес', 'error')
            return redirect(url_for('location'))
        print(f"Адрес пользователя: {geocode}")
        server_address = 'http://geocode-maps.yandex.ru/1.x/?'
        api_key = 'c514a804-086f-4788-9357-4ac645d35c74'

        geocoder_request = f'{server_address}apikey={api_key}&geocode=Великий Новгород,{geocode}&format=json'

        response = requests.get(geocoder_request)
        if not response:
            geocoder_request = f'{server_address}apikey={api_key}&geocode=Новгородская область,{geocode}&format=json'
            response = requests.get(geocoder_request)
        if response:
            json_response = response.json()

            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

            toponym_coodrinates = toponym["Point"]["pos"]

            print(toponym_address, "имеет координаты:", toponym_coodrinates)
            toponym_longitude1 = toponym_coodrinates.split()[0]
            toponym_lattitude1 = toponym_coodrinates.split()[1]
            print(toponym_longitude1, toponym_lattitude1)
            api_server = 'https://static-maps.yandex.ru/v1?'
            toponym_longitude = 31.253898
            toponym_lattitude = 58.525216

            API_KEY = "c7e6930c-2621-45c2-9bf7-3b85675e054c"
            pt = ",".join([str(toponym_longitude), str(toponym_lattitude), str('pm2dbm')]) + '~' + ",".join(
                [str(toponym_longitude1), str(toponym_lattitude1), str('pm2wtm')])
            print(pt)
            params = {
                "apikey": API_KEY,
                "ll": ",".join([str(toponym_longitude), str(toponym_lattitude)]),
                "pt": ",".join([str(toponym_longitude), str(toponym_lattitude), str('pm2dbm')]) + '~' + ",".join(
                    [str(toponym_longitude1), str(toponym_lattitude1), str('pm2wtm')]),
            }

            response = requests.get(api_server, params=params)

            if not response:
                print("Ошибка выполнения запроса:")
                print(response)
                print("Http статус:", response.status_code, "(", response.reason, ")")

            map_file = "static/upload/map.png"
            with open(map_file, "wb") as file:
                file.write(response.content)
    return render_template('location.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            if current_user.id == 1:
                return redirect("/admin")
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.phone_number = form.phone_number.data
        user.email = form.email.data
        user.set_password(form.password.data)
        print(user)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/discountcard')
def discountcard():
    return render_template('discountcard.html')


@app.route('/admin')
def admin():
    if current_user.id == 1:
        return render_template('admin.html')
    return redirect('/')


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()
