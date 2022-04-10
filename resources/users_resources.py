from datetime import datetime

from flask import jsonify
from flask_restful import Resource, abort, reqparse

from data import db_session
from data.users import User


def abort_if_users_not_found(users_id):
    session = db_session.create_session()
    news = session.query(User).get(users_id)
    if not news:
        abort(404, message=f"User {users_id} not found")


class UsersResource(Resource):
    def get(self, users_id):
        abort_if_users_not_found(users_id)
        session = db_session.create_session()
        news = session.query(User).get(users_id)
        return jsonify({'user': news.to_dict(
            only=("id", "name", "email", "link", "authentication", "created_date", "news",
                  "admin"))})

    def delete(self, users_id):
        abort_if_users_not_found(users_id)
        session = db_session.create_session()
        news = session.query(User).get(users_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=("id", "name", "email", "link", "authentication", "created_date", "news",
                  "admin")) for item in users]})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('email', required=True)
        parser.add_argument('link', required=True)
        parser.add_argument('authentication', required=True, type=bool)
        parser.add_argument('admin', required=True, type=int)
        parser.add_argument('password', required=True)
        parser.add_argument("avatar", required=True)
        args = parser.parse_args()
        session = db_session.create_session()
        news = User(
            id=args["id"],
            name=args["name"],
            email=args["email"],
            link=args["link"],
            authentication=args["authentication"],
            created_date=datetime.now(),
            admin=args["admin"],
            avatar="/static/images/defoult.png"
        )
        news.set_password(args["password"])
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})
