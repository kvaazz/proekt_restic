from flask_login import current_user
from flask import Flask, render_template, url_for, request, redirect
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user
from data.Forms import LoginForm, RegisterForm
from data.users import User
from data.dishes import Dish
import requests
from werkzeug.utils import secure_filename
import time
from pathlib import Path
import barcode
from barcode.writer import ImageWriter
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

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

        EAN = barcode.get_barcode_class('code128')
        my_barcode = EAN(user.email, writer=ImageWriter())
        file_path = Path('static') / 'img' / 'cards' / user.email
        my_barcode.save(file_path)
        user.card = user.email

        print(user)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/menu')
def menu():
    CATEGORIES = {
        'all': 'Все',
        'salads': 'Салаты',
        'soups': 'Супы',
        'mains': 'Горячее',
        'desserts': 'Десерты',
        'drinks': 'Напитки'
    }
    current_category = request.args.get('category', 'all')

    db_sess = db_session.create_session()

    if current_category == 'all':
        dishes = db_sess.query(Dish).all()
    else:
        dishes = db_sess.query(Dish).filter(Dish.category == current_category).all()

    menu_data = {
        'title': 'Меню',
        'dishes': dishes,
        'categories': CATEGORIES,
        'current_category': current_category
    }

    return render_template('menu.html', menu=menu_data)


@app.route('/discountcard')
def discountcard():
    card_image = f"img/cards/{current_user.card}.png"
    return render_template('discountcard.html',
                           card_image=card_image)


@app.route('/admin')
def admin():
    if current_user.id == 1:
        CATEGORIES = {
            'all': 'Все',
            'salads': 'Салаты',
            'soups': 'Супы',
            'mains': 'Горячее',
            'desserts': 'Десерты',
            'drinks': 'Напитки'
        }
        current_category = request.args.get('category', 'all')

        db_sess = db_session.create_session()

        if current_category == 'all':
            dishes = db_sess.query(Dish).all()
        else:
            dishes = db_sess.query(Dish).filter(Dish.category == current_category).all()

        menu_data = {
            'title': 'Меню',
            'dishes': dishes,
            'categories': CATEGORIES,
            'current_category': current_category
        }

        return render_template('admin.html', menu=menu_data)

    return redirect('/')


@app.route('/admin/add_dish', methods=['GET', 'POST'])
def admin_add():
    if current_user.id == 1:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')
            category = request.form.get('category')

            if not all([name, description, price]):
                return redirect(url_for('admin_add'))

            image_filename = 'default.jpg'
            if 'image' in request.files:
                file = request.files['image']

                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"{int(time.time())}_{filename}"
                    file_path = Path('static') / 'img' / filename
                    file.save(str(file_path))
                    saved_filename = filename

                    if saved_filename:
                        image_filename = saved_filename

            db_sess = db_session.create_session()
            dish = Dish()
            dish.name = name.strip()
            dish.description = description.strip()
            dish.price = price
            dish.image = image_filename
            dish.category = category
            db_sess.add(dish)
            db_sess.commit()
            return redirect(url_for('admin'))
        return render_template('add_dish.html')
    return redirect('/')


@app.route('/admin/edit_dish/<int:dish_id>', methods=['GET', 'POST'])
def admin_edit(dish_id):
    if current_user.id == 1:
        db_sess = db_session.create_session()
        dish = db_sess.query(Dish).get(dish_id)

        if not dish:
            return redirect(url_for('admin'))

        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')
            category = request.form.get('category')

            price = int(price)

            dish.name = name.strip()
            dish.description = description.strip()
            dish.price = price
            dish.category = category

            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    from werkzeug.utils import secure_filename
                    from pathlib import Path
                    import time

                    filename = secure_filename(file.filename)
                    filename = f"{int(time.time())}_{filename}"
                    file_path = Path('static') / 'img' / filename

                    if dish.image and dish.image != 'default.jpg':
                        old_path = Path('static') / 'img' / dish.image
                        if old_path.exists():
                            old_path.unlink()

                    file.save(str(file_path))
                    dish.image = filename

            db_sess.commit()
            return redirect(url_for('admin'))

        return render_template('edit_dish.html', title='Изменить блюдо', dish=dish)

    return redirect('/')


@app.route('/admin/delete_dish', methods=['GET', 'POST'])
def admin_delete():
    if current_user.id == 1:
        dish_id = request.form.get('dish_id')

        if not dish_id:
            return redirect(url_for('admin'))

        db_sess = db_session.create_session()
        dish = db_sess.query(Dish).get(dish_id)

        if not dish:
            return redirect(url_for('admin'))

        if dish.image and dish.image != 'default.jpg':
            from pathlib import Path
            image_path = Path('static') / 'img' / dish.image
            if image_path.exists():
                image_path.unlink()

        db_sess.delete(dish)
        db_sess.commit()

        return redirect(url_for('admin'))

    return redirect('/')


def main():
    db_session.global_init("db/users.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
