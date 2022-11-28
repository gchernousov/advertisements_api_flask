from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_bcrypt import Bcrypt

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, create_engine, func
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

import os
from dotenv import load_dotenv

from validators import HttpError, validate, CreateUserScheme, CreateAdvertisementScheme
from functions import users_list, advertisements_list


app = Flask('advert_app')
bcrypt = Bcrypt(app)

# environment variables
load_dotenv()
db_name = os.getenv('POSTGRES_DB')
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('HOST')
db_port = os.getenv('PORT')

DSN = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# PERMISSIONS
@app.errorhandler(HttpError)
def invalid_usage(error: HttpError):
    response = jsonify({'status': 'ERROR', 'message': error.message})
    response.status_code = error.status_code
    return response


def authentication(headers):
    """Проверка логина и пароля"""
    data = dict(headers)
    if 'Login' in data.keys() and 'Password' in data.keys():
        with Session() as session:
            user = session.query(UserModel).filter(UserModel.username == data['Login']).first()
            if user is None:
                raise HttpError(404, 'user is not found')
            if bcrypt.check_password_hash(user.password, data['Password']) is False:
                raise HttpError(401, 'password don\'t match, permission denied')
    else:
        raise HttpError(401, 'not authenticated')
    return user.id


def permission(user_id, adv_id):
    """Проверка владельца объявления"""
    with Session() as session:
        advertisement = session.query(AdvertisementModel).get(adv_id)
        if user_id != advertisement.id_user:
            raise HttpError(403, 'it\' not your advertisement, permission denied')


# MODELS
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    password = Column(String, nullable=False)
    registration_time = Column(DateTime, server_default=func.now())
    email = Column(String, unique=True)
    advertisements = relationship('AdvertisementModel', backref='user')

    @classmethod
    def registration(cls, session: Session, username: str, password: str, email: str):
        new_user = UserModel(
            username=username,
            password=bcrypt.generate_password_hash(password).decode('utf-8'),
            email=email
        )
        session.add(new_user)
        try:
            session.commit()
            return new_user
        except IntegrityError:
            session.rollback()
            raise HttpError(400, 'user already exists')


class AdvertisementModel(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    created = Column(DateTime, server_default=func.now())
    id_user = Column(Integer, ForeignKey('users.id'))


Base.metadata.create_all(engine)


# VIEWS
def check():
    return jsonify({'status': 'OK'})


class UserView(MethodView):

    def get(self, user_id=None):
        if user_id is None:
            with Session() as session:
                users = session.query(UserModel).all()
                usr_lst = users_list(users)
                return jsonify({'users': usr_lst})
        else:
            with Session() as session:
                user = session.query(UserModel).get(user_id)
                if user is None:
                    raise HttpError(404, 'user is not found')
                adv_list = advertisements_list(user.advertisements)
                return jsonify({'username': user.username,
                                'email': user.email,
                                'registration time': user.registration_time,
                                'advertisements': adv_list})

    def post(self):
        with Session() as session:
            val_data = validate(request.json, CreateUserScheme)
            new_user = UserModel.registration(session, **val_data)
            return jsonify({'status': 'new user registration successfully',
                            'user id': new_user.id})


class AdvertisementsView(MethodView):

    def get(self, advert_id=None):
        if advert_id is None:
            with Session() as session:
                advertisements = session.query(AdvertisementModel).all()
                adv_list = advertisements_list(advertisements)
                return jsonify({'advertisements': adv_list, 'count': len(advertisements)})
        else:
            with Session() as session:
                advertisement = session.query(AdvertisementModel).get(advert_id)
                if advertisement is None:
                    raise HttpError(404, 'advertisement is not found')
                return jsonify({'title': advertisement.title,
                                'description': advertisement.description,
                                'created': advertisement.created,
                                'user': advertisement.id_user})

    def post(self):
        new_data = request.json
        user_id = authentication(request.headers)
        new_data['id_user'] = user_id
        with Session() as session:
            val_data = validate(new_data, CreateAdvertisementScheme)
            new_advertisement = AdvertisementModel(**val_data)
            session.add(new_advertisement)
            session.commit()
            return jsonify({'status': 'new advertisement added successfully',
                            'advertisement id': new_advertisement.id})

    def patch(self, advert_id: int):
        user_id = authentication(request.headers)
        permission(user_id, advert_id)
        patch_data = request.json
        with Session() as session:
            adv = session.query(AdvertisementModel).get(advert_id)
            for field, value in patch_data.items():
                setattr(adv, field, value)
            session.commit()
            return jsonify({'status': 'advertisement is changed'})

    def delete(self, advert_id: int):
        user_id = authentication(request.headers)
        permission(user_id, advert_id)
        with Session() as session:
            adv = session.query(AdvertisementModel).get(advert_id)
            session.delete(adv)
            session.commit()
            return jsonify({'status': 'advertisement is delete'})


# URLS
app.add_url_rule('/', view_func=check, methods=['GET'])
app.add_url_rule('/user/<int:user_id>', view_func=UserView.as_view('user_detail'), methods=['GET'])
app.add_url_rule('/user/', view_func=UserView.as_view('users'), methods=['GET', 'POST'])
app.add_url_rule('/advertisement/<int:advert_id>',
                 view_func=AdvertisementsView.as_view('advertisement_detail'),
                 methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/advertisement/',
                 view_func=AdvertisementsView.as_view('advertisements'),
                 methods=['GET', 'POST'])


if __name__ == "__main__":
    app.run()
