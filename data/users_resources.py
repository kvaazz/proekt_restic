from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from . import db_session
from .users import User


def abort_if_user_not_found(news_id):
    session = db_session.create_session()
    news = session.query(User).get(news_id)
    if not news:
        abort(404, message=f"User {news_id} not found")

parser = reqparse.RequestParser()
parser.add_argument('id', type=int)
parser.add_argument('surname', required=True)
parser.add_argument('age', required=True, type=int)
parser.add_argument('name', required=True)
parser.add_argument('position', required=True)
parser.add_argument('speciality', required=True)
parser.add_argument('address', required=True)
parser.add_argument('email', required=True)
parser.add_argument('modified_date')
parser.add_argument('hashed_password')

class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        return jsonify({'users': user.to_dict(
            only=('id', 'surname', 'age', 'name', 'position', 'speciality', 'address', 'email', 'modified_date'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id',
                  'surname',
                  'age',
                  'name',
                  'position',
                  'speciality',
                  'address',
                  'email',
                  'modified_date')) for item in user]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User()
        user.surname = args["surname"]
        user.name = args["name"]
        user.age = args["age"]
        user.position = args["position"]
        user.speciality = args["speciality"]
        user.address = args["address"]
        user.email = args["email"]
        user.set_password(args["hashed_password"])
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})