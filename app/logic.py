from flask import session, request
from app.models import session_db, User, Post
from config import *
__author__ = 'mg'

def get_user_from_session_and_cookies():
    user = None
    if 'user' in session:
        user = session['user']

    if 'user' in request.cookies:
        user_in_database = session_db.query(User).filter(User.login == request.cookies['user']).first()
        if user_in_database.password == request.cookies['password']:
            session['user'] = {'login':user_in_database.login,
                                'e_mail':user_in_database.e_mail,
                                'role':user_in_database.role,
                                'info':user_in_database.info}
            user = request.cookies['user']


    # print(user)
    return user



def get_last_posts(username, number):
    posts = session_db.query(Post).filter(Post.user_login==username).order_by(Post.id.desc()).all()
    posts = posts[:number:]
    for post in posts:
        post.delete_tag_chars()
    return posts

def allowed_file(filename):
    return '.' in filename and\
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

