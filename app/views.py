from flask import render_template, flash, redirect, request, session, url_for, g, make_response, send_from_directory, g

from app import app
from app.forms import LoginForm
from app.models import User, session_db, Post, Subscription
from hashlib import md5
from datetime import datetime
from app.logic import *
import os
from werkzeug.utils import secure_filename

@app.before_first_request
def set_session():
    get_user_from_session_and_cookies()
    # return redirect(url_for('users'))

@app.route('/')
@app.route('/index')
def index():
    posts = session_db.query(Post).order_by(Post.id.desc()).all()
    posts = posts[:10:]
    user = get_user_from_session_and_cookies()
    return render_template('index.html',
                           title='Home',
                           posts=posts)




@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    #print(request.cookies.get('user', 'нету'))
    form = LoginForm(request.form)
    user = get_user_from_session_and_cookies()
    if user:
        return redirect(url_for('index'))


    if request.method == 'POST' and form.validate():

        try:
            user_md5 = md5()
            user_md5.update(bytearray(form.password.data, 'utf8'))
            user_password = user_md5.hexdigest()
            user = User(form.login.data, user_password, None)
            session_db.add(user)
            session_db.commit()
            flash('Login requested by login="' + form.login.data + '", remember me=' + str(form.remember_me.data))
            session['user'] = {'login':user.login, 'e_mail':user.e_mail, 'role':user.role}
            response = make_response(redirect(url_for('get_user', username=user.login)))
            if form.remember_me.data:
                response.set_cookie('user', user.login, max_age=157680000)
                response.set_cookie('password', user.password, max_age=157680000)

            return response
        except:
            session_db.rollback()
            flash('The user is already exists, ' + str(session_db.query(User).filter(User.role == 1).all()))
            return redirect(url_for('sign_up'))

    return render_template('login.html',
                           method=request.method,
                           title='Sign Up',
                           form=form,
                           page = '/signup')



@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_user_from_session_and_cookies()
    if user:
        return redirect(url_for('index'))

    form = LoginForm(request.form)

    if request.method == 'POST':
        user_md5 = md5()
        user_md5.update(bytearray(form.password.data, 'utf8'))
        user_password = user_md5.hexdigest()
        user = session_db.query(User).filter(User.login == form.login.data).filter(
                                             User.password == user_password).first()
        if user:
            response = make_response(redirect(url_for('get_user', username=user.login)))
            if form.remember_me.data:
                response.set_cookie('user', user.login, max_age=157680000)
                response.set_cookie('password', user.password, max_age=157680000)
            session['user'] = {'login':user.login, 'e_mail':user.e_mail, 'role':user.role}
            flash('Hi, %s' % (user.login))
            return response
        flash('User %s does not exists or password is wrong' % form.login.data)
        return redirect(url_for('login'))
    return render_template('login.html',
                           method = request.method,
                           title='Log In',
                           form=form,
                           page='login')




@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    if 'user' in session.keys():
        session.pop('user')
    if 'user' in request.cookies:
        response.set_cookie('user', '', max_age=0)
        response.set_cookie('password', '', max_age=0)
    return response


@app.route('/post', methods=['POST'])
def make_post():
    if 'user' not in session:
        return redirect(url_for('index'))
    post = request.form.get('text_post')
    if post and len(post) < 250:
        post = Post(post, datetime.now(), session['user']['login'])
        session_db.add(post)
        session_db.commit()
        return redirect(url_for('get_user', username=session['user']['login']))
    flash('Post must be not empty and > 250 characters')
    return redirect(url_for('get_user', username=session['user']['login']))



@app.route('/Subscribe', methods=['POST'])
def subscribe():
    # print(request.form['user_login'])
    if 'user' not in session:
        return redirect(url_for('user', username=request.form['user_login']))

    sub = Subscription(session['user']['login'], request.form['user_login'])
    session_db.add(sub)
    session_db.commit()

    return redirect(url_for('get_user', username=request.form['user_login']))


@app.route('/Unsubscribe', methods=['POST'])
def unsubscribe():
    # print(request.form['user_login'])
    if 'user' not in session:
        return redirect(url_for('user', username=request.form['user_login']))
    # try:
    sub = Subscription(session['user']['login'], request.form['user_login'])
    # print(sub)
    session_db.query(Subscription).filter(Subscription.follower == sub.follower)\
        .filter(Subscription.blog == sub.blog).delete()
    session_db.commit()
    # except:pass
    return redirect(url_for('get_user', username=request.form['user_login']))


@app.route('/user/<username>', methods=['GET', 'POST'])
def get_user(username):
    number_of_posts = 10;

    user = session_db.query(User).filter(User.login == username).first()
    if not user:
        return redirect(url_for('index'))



    if request.method == 'POST':
            number_of_posts = int(request.form['number_of_posts']) + 10


    # print(number_of_posts)
    posts = get_last_posts(username, number_of_posts)
    if username != session.get('user', {}).get('login', None):
        subscribed = 'Disabled'
        if 'user' in session:
            subscribed = session_db.query(Subscription).filter(Subscription.follower == session['user']['login'])\
                .filter(Subscription.blog == username).first()
            # print(subscribed)
            subscribed = 'Unsubscribe' if subscribed else 'Subscribe'


        return render_template('user.html',
                           user=user,
                           posts=posts,
                           subscribed=subscribed,
                           disabled='disabled' if subscribed == 'Disabled' else '',
                           number_of_posts=number_of_posts)
    return render_template('main_user.html',
                           user=user,
                           posts=posts,
                           number_of_posts=number_of_posts)

@app.route('/user/<username>/subscriptions')
def subs(username):
     if 'user' not in session:
        return redirect(url_for('index'))
     users_subscriptions = session_db.query(User)\
         .select_from(Subscription)\
         .filter(Subscription.follower == username)\
         .join(User, Subscription.blog == User.login).all()
     return render_template('subscriptions.html',
                            users=users_subscriptions)

@app.route('/feed', methods=['GET', 'POST'])
def feed():
    if 'user' not in session:
        return redirect(url_for('index'))
    number_of_posts = 10
    if request.method == 'POST':
        number_of_posts = int(request.form['number_of_posts']) + 10
    users_subscriptions = session_db.query(Subscription.blog)\
        .filter(Subscription.follower == session['user']['login'])\
        .all()
    # print(users_subscriptions[0][0])
    # users_subscriptions = [user[0] for user in users_subscriptions]
    # print(users_subscriptions)
    posts = session_db.query(Post)\
        .filter(Post.user_login.in_(users_subscriptions))\
        .order_by(Post.id.desc())\
        .all()
    # print('posts ', posts)
    posts = posts[:number_of_posts]
    return render_template('feed.html',
                           posts=posts,
                           number_of_posts=number_of_posts)


@app.route('/change_info', methods=['POST'])
def change_info():
    if 'user' not in session:
        return redirect(url_for('index'))
    user = session_db.query(User).filter(User.login == session['user']['login']).first()
    user.info = request.form['info']
    #print(user.info)
    session_db.commit()
    return redirect(url_for('get_user', username=session['user']['login']))

@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('settings.html')

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user' not in session:
        return redirect(url_for('index'))
    user_md5 = md5()
    user_md5.update(bytearray(request.form['old_password'], 'utf8'))
    old_password = user_md5.hexdigest()
    user = session_db.query(User).filter(User.login == session['user']['login']).first()
    if old_password != user.password:
        flash('Password is wrong!')
        return redirect(url_for('settings'))
    new_password = request.form['new_password']
    if new_password != request.form['new_password_again']:
        flash('Repeat new password, please!')
        return redirect(url_for(settings))
    user_md5.update(bytearray(new_password, 'utf8'))
    user.password = user_md5.hexdigest()
    session_db.commit()
    flash('Successfully!')
    response = make_response(url_for('settings'))
    response.set_cookie('password', user.password, max_age=157680000)
    return response

@app.route('/load_avatar', methods=['POST'])
def upload_file():
    if 'user' not in session:
        return request(url_for('index'))
    file=request.files['avatar']
    if file and allowed_file(file.filename):
        # print(os.listdir(UPLOAD_FOLDER))
        files_in_directory = [f for f in os.listdir(UPLOAD_FOLDER) if f.rsplit('.', 1)[0] == session['user']['login']]
        # print(files_in_directory)
        for file_previous in files_in_directory:
            os.remove(os.path.join(UPLOAD_FOLDER, file_previous))
        filename = session['user']['login'] + '.' + file.filename.rsplit('.', 1)[1]
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        flash('Successfully!')
    # print('!!!')
    response = make_response(redirect(url_for('get_user', username=session['user']['login'])))
    return response

@app.route('/avatar/<username>')
def avatar(username):
    file = [f for f in os.listdir(UPLOAD_FOLDER) if f.rsplit('.', 1)[0] == username]
    # print('filec ' + file[0])
    return send_from_directory(UPLOAD_FOLDER, file[0])

@app.route('/users', methods=['GET', 'POST'])
def get_users():
    users = session_db.query(User).order_by(User.login).all()
    number_of_posts = 10
    if request.method == 'POST':
        number_of_posts = int(request.form['number_of_posts']) + 10
    users = users[:number_of_posts]
    return render_template('users.html',
                           users=users,
                           number_of_posts=number_of_posts)

@app.route('/delete_post', methods=['POST'])
def delete_post():
    if 'user' not in session:
        return redirect(url_for('index'))
    session_db.query(Post).filter(Post.id == request.form['id']).delete()
    session_db.commit()
    return redirect(url_for('get_user', username=session['user']['login']))

@app.route('/find_user', methods=['POST'])
def find_user():
    return redirect(url_for('get_user', username=request.form['user']))