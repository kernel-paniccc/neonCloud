from flask import request, render_template, redirect, flash, session, send_file
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from main_mod import app, db
from main_mod.models import User, get_info, generate_random_string
from main_mod.mail_send import send_ya_mail
import os


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
    if current_user.is_authenticated:
        logout_user()
    if session.get('username'):
        session.pop('username')

    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['id'] = user.id
        session['username'] = user.username

        return redirect('/2fa')
    else:
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
        code = generate_random_string(12)
        session['2fa'] = code
        send_ya_mail(str(session['email']), f'You secret code for 2FA: {code}')
        flash("токен отправлен на почту", category='success')
        return redirect('/2fa')
    except KeyError:
        return redirect('/')


@app.route('/2fa', methods=['GET', 'POST'])
def two_factor():
    try:
        if not(session.get('username')):
            flash('вы не зарегистрированы', category='error')
            return redirect('/login')
        username = session['username']
        user = User.query.filter_by(username=username).first()
        token = request.form.get('token')
        email = user.email
        session['email'] = email
        code = session['2fa']
        if str(token) == str(code):
            login_user(user)
            session.pop('2fa')
            session.pop('email')
            code = None
            return redirect('/')
        else:
            if (token != None and code != None) and str(token) != str(code):
                flash("неверный токен авторизации", category='error')
        return render_template('2fa.html')
    except KeyError:
        return render_template('2fa.html')



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


