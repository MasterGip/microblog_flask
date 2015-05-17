__author__ = 'mg'

from app import db_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import mapper, sessionmaker

ROLE_USER = 0
ROLE_ADMIN = 1


metadata = MetaData()
metadata.reflect(bind=db_engine)

#Классы сущностей
class User:
    def __init__(self, login, password, e_mail, info='', role=0):
        self.login = login
        self.password = password
        self.e_mail = e_mail
        self.role = role
        self.info = info

    def __repr__(self):
        return '<User(\'%s\' ,\'%s\', \'%s\', \'%s\')>' % (self.login,
                                                           self.password,
                                                           self.e_mail,
                                                           self.role)


class Post:
    def __init__(self, body, time_post, user_login):
        self.body = body
        self.time_post = time_post
        self.user_login = user_login

    def delete_tag_chars(self):
        self.body.replace('<','&lt;')
        self.body.replace('>', '&gt;')

    def __repr__(self):
        return '<Post(\'%s\' ,\'%s\', \'%s\', \'%s\')>' % (self.id,
                                                           self.body,
                                                           self.time_post,
                                                           self.user_login)

class Subscription:
    def __init__(self, follower, blog):
        self.follower = follower
        self.blog = blog

    def __repr__(self):
        return '<Subscription(\'%s\' ,\'%s\')' % (self.follower,
                                                 self.blog)
#Привязка к БД
mapper(User, metadata.tables['login_password'])
mapper(Post, metadata.tables['posts'])
mapper(Subscription, metadata.tables['subscriptions'])

#Открываем сессию
Session = sessionmaker(bind=db_engine)
session_db = Session()


