from flask import request, render_template, redirect, flash, session
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from main_mod import app, db
from main_mod.models import User
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_return = request.form['password_return']
        if password != password_return:
            flash('пароли не совпадают ', category='error')
        else:
            pass_hash = generate_password_hash(password)
            new_user = User(username=username, password=pass_hash)
            db.session.add(new_user)
            db.session.commit()

            return redirect("/login")
    return render_template("register_page.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        session['id'] = user.id
        session['username'] = user.username

        return redirect('/')
    else:
        flash('некорректные данные', category='error')

    return render_template('login_page.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect('/login')
    return response


