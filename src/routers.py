from flask import request, render_template, redirect, flash, session, send_file
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import os

from src import app, db
from src.mail_send import send_ya_mail
from src.models import User, get_info, generate_random_string


@app.route('/', methods=['GET', 'POST'])
@login_required
def main():
    username = str(session['username'])
    if request.method == 'POST':
        file = request.files['file']
        if 'file' not in request.files or file.filename == '':
            flash("ошибка отправки", category="error")
        else:
            flash("отправка успешна", category='success')
            id = session['id']
            if os.path.isdir(f'user_files/{str(id)}'):
                file.save(f'user_files/{str(id)}/{file.filename}')
            else:
                os.mkdir(f'user_files/{str(id)}')
                file.save(f'user_files/{str(id)}/{file.filename}')
    return render_template("index.html", username=username)


@app.route('/registration', methods=['GET', 'POST'])
def register():
    session.clear()
    if current_user.is_authenticated:
        logout_user()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_return = request.form['password_return']
        try:
            if password != password_return:
                flash('пароли не совпадают ', category='error')
            elif "@" not in str(email):
                flash('неверный адрес почты ', category='error')
            else:
                pass_hash = generate_password_hash(password)
                new_user = User(username=username, password=pass_hash, email=email)
                db.session.add(new_user)
                db.session.commit()
                return redirect("/login")
        except:
            flash("имя пользователя уже занято", category='error')
    return render_template("register_page.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if current_user.is_authenticated:
        logout_user()
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['id'] = user.id
        session['username'] = user.username

        return redirect('/2fa')
    elif user != password:
        flash('некорректные данные', category='error')
    return render_template('login_page.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/send', methods=['GET', 'POST'])
def send_msg():
    try:
        if current_user.is_authenticated:
            logout_user()
        session['2fa'] = generate_random_string(12)
        send_ya_mail(str(session['email']), f'You secret code for 2FA: {str(session["2fa"])}')
        flash("токен отправлен на почту", category='success')
        return redirect('/2fa')
    except KeyError:
        return redirect('/')


@app.route('/2fa', methods=['GET', 'POST'])
def two_factor():
    try:
        if current_user.is_authenticated:
            logout_user()
        if not(session.get('username')):
            flash('вы не зарегистрированы', category='error')
            return redirect('/login')
        user = User.query.filter_by(username=session['username']).first()
        token = request.form.get('token')
        session['email'] = user.email
        if str(token) == str(session['2fa']):
            login_user(user)
            session.pop('2fa'), session.pop('email')
            return redirect('/')
        elif (token != None and session['2fa'] != None) and str(token) != str(session['2fa']):
            flash("неверный токен авторизации", category='error')
        return render_template('2fa.html')
    except KeyError:
        return render_template('2fa.html')

@app.route('/forgot_pass', methods=['GET', 'POST'])
def forgot_password():
    try:
        if current_user.is_authenticated:
            logout_user()
        username = request.form.get('username')
        token = request.form.get('token')
        if request.method == 'POST':
            if token == None:
                session['username'] = username
                code = generate_random_string(20)
                session['code'] = code
                user = User.query.filter_by(username=username).first()
                send_ya_mail(str(user.email), f'You token for reset password: {str(code)}')
                flash("токен отправлен на почту", category='success')
            code = session['code']
            if str(token) == str(code):
                session.pop('code')
                session['redirect'] = session['username']
                return redirect(f'/new_pass_for/{session["username"]}')
            elif (token != None and code != None) and str(token) != str(code):
                flash("неверный токен авторизации", category='error')
    except AttributeError:
        if username != None:
            flash('пользователь не найден', category='error')
    except KeyError:
        return redirect('/')
    return render_template('get_pass_token.html')

@app.route('/new_pass_for/<path:name>', methods=['GET', 'POST'])
def refactor_user_password(name):
    try:
        if session['redirect'] != name:
            flash('вы не зарегистрированны', category='error')
            return redirect('/login')
        if current_user.is_authenticated:
            logout_user()
        user = User.query.filter_by(username=name).first()
        if request.method == 'POST':
            password = request.form.get('password')
            password_return = request.form.get('password_return')
            if password != password_return:
                flash('пароли не совпадают ', category='error')
            if password == password_return:
                pass_hash = generate_password_hash(password)
                user.password = pass_hash
                db.session.commit()
                flash('пароль изменен ', category='success')
                session.pop('redirect')
                return redirect('/login')
    except KeyError:
        flash('вы не зарегистрированны', category='error')
        return redirect('/login')
    return render_template('reset_password.html')


@app.route('/get_file/',  methods=['GET', 'POST'], defaults={'reqPath': ''})
@app.route('/get_file/<path:reqPath>')
@login_required
def get_file(reqPath):
    try:
        id = session['id']
        abs_path = f'user_files/{str(id)}/{str(reqPath)}'
        dir = f'user_files/{str(id)}'
        if os.path.isfile(abs_path):
            return send_file(f"../{str(abs_path)}")

        all_files = os.scandir(f'user_files/{str(id)}')
        files = [get_info(x) for x in all_files]
        if len(os.listdir(dir)) == 0:
            flash('ваша папка пуста', category='error')
            return redirect('/')
        return render_template('file_page.html', file=files)
    except FileNotFoundError:
        flash('ваша папка пуста', category='error')
        return redirect('/')


@app.route('/del')
@app.route('/del/<path:name>')
@login_required
def delited(name):
    try:
        id = session['id']
        path = f'user_files/{str(id)}/{str(name)}'
        os.remove(path)
        return redirect('/get_file')
    except OSError:
        return redirect('/')


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect('/login')
    return response


