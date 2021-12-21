from flask import Flask, render_template, request, flash, redirect, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, UserMixin, current_user, logout_user
from login import UserLogin
import db
import bitlyshortener

access_tokens = ["e072a07589e2f937689389b5266dd6f1e6e113bd"]
app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = ""
login_manager.login_message = 'Пройдите авторизацию!'
header_left = [{"title": "Главная", "url": "/"},
               {"title": "Сокращатель", "url": "/shortener"}]

header_right = [{"title": "Авторизация", "url": "/login"}]

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, db)

@app.route("/")
def index():
    con = db.sqlite3.connect('shortener.db')
    cursor = con.cursor()
    cursor.execute("""SELECT short_link, long_link FROM user_links where private_id=1;""")
    data = cursor.fetchall()
    general_links = []
    authorized_links = []

    for d in data:
        general_link = {}
        general_link["long_link"] = d[1]
        general_link["short_link"] = d[0]
        general_links.append(general_link)

    if current_user.is_authenticated:
        cursor.execute("""SELECT short_link, long_link FROM user_links where private_id=3;""")

        data = cursor.fetchall()
        for d in data:
            authorized_link = {}
            authorized_link["long_link"] = d[1]
            authorized_link["short_link"] = d[0]
            authorized_links.append(authorized_link)
    else:
        authorized_links = ["Авторизируйтесь, чтобы увидеть ссылки!"]

    if current_user.is_authenticated:
        header_right = [{"title": "Выйти", "url": "/logout"}, {"title": "Мои ссылки", "url": "/links"}]
        return render_template('index.html', header_left=header_left, header_right=header_right, general_links = general_links, authorized_links = authorized_links)
    else:
        header_right = [{"title": "Авторизация", "url": "/login"}]
        return render_template('index.html', header_left=header_left, header_right=header_right, general_links = general_links, authorized_links = authorized_links)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = db.getUserByEmail(request.form['email'])
        if not user:
            flash("Пользователь не найден!")
        elif user and check_password_hash(user[3], request.form['password']):
            userLogin = UserLogin().create(user)
            login_user(userLogin)
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль!')
    else:
        flash('Ошибка авторизации!')
    if current_user.is_authenticated:
        header_right = [{"title": "Выйти", "url": "/logout"}, {"title": "Мои ссылки", "url": "/links"}]
        return render_template('login.html', header_left=header_left, header_right=header_right)
    else:
        header_right = [{"title": "Авторизация", "url": "/login"}]
        flash("")
        return render_template('login.html', header_left=header_left, header_right=header_right)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта!", "success")
    return redirect(url_for('login'))

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        con = db.sqlite3.connect('shortener.db')
        cursor = con.cursor()
        cursor.execute("""SELECT email FROM users where email=?;""", (request.form['email'],))
        data = cursor.fetchall()
        if request.form['password'] == request.form['password_check']:
            if len(data) < 1:
                hash = generate_password_hash(request.form['password'])
                db.create_user(request.form['name'], request.form['email'], hash)
                flash("Вы успешно зарегистрировались!", "success")
                return redirect(url_for('login'))
            else:
                flash("Такой пользователь уже зарегистрирован!", "success")
        else:
            flash("Пароли не совпадают!", "success")
    else:
        flash("Ошибка регистрации!", "success")

    if current_user.is_authenticated:
        header_right = [{"title": "Выйти", "url": "/logout"}, {"title": "Мои ссылки", "url": "/links"}]
        return render_template('register.html', header_left=header_left, header_right=header_right)
    else:
        header_right = [{"title": "Авторизация", "url": "/login"}]
        return render_template('register.html', header_left=header_left, header_right=header_right)

@app.route("/links", methods=["POST", "GET"])
@login_required
def links():
    if request.method == "POST":
        db.delete_link(current_user.get_id(), request.form['delete'])
        redirect(url_for('links'))

    con = db.sqlite3.connect('shortener.db')
    cursor = con.cursor()
    cursor.execute("""SELECT short_link, private_id, long_link FROM user_links where user_id=?;""", (current_user.get_id(),))
    data_links = cursor.fetchall()

    links = []
    link_type = [{"link_type_id": 1, "link_type": "Общедоступная"},
                 {"link_type_id": 2, "link_type": "Приватная"},
                 {"link_type_id": 3, "link_type": "Для авторизированных"}]
    for d in data_links:
        con = db.sqlite3.connect('shortener.db')
        cursor = con.cursor()
        cursor.execute("""SELECT id, private_id FROM user_links where user_id=? and short_link=? and private_id=?;""", (current_user.get_id(), d[0], d[1]))
        data2 = cursor.fetchall()
        for d2 in data2:
            user_links = {}
            user_links["short_link"] = d[0]
            user_links["long_link"] = d[2]
            user_links["id"] = d2[0]
            user_links["type_id"] = d2[1]
            print(links)
            links.append(user_links)


    if current_user.is_authenticated:
        header_right = [{"title": "Выйти", "url": "/logout"}, {"title": "Мои ссылки", "url": "/links"}]
        return render_template('links.html', header_left=header_left, header_right=header_right, links=links, link_type = link_type)
    else:
        header_right = [{"title": "Авторизация", "url": "/login"}]
        return render_template('links.html', header_left=header_left, header_right=header_right, links=links, link_type = link_type)

@app.route("/change_link", methods=["POST", "GET"])
def change_link():
    if request.method == "POST":
        con = db.sqlite3.connect('shortener.db')
        cursor = con.cursor()
        cursor.execute("""UPDATE user_links SET private_id=? WHERE id=?;""", (request.form['change_link_type'], request.form['change_link_id']))
        con.commit()
        print(request.form['change_link_type'])
        print(request.form['change_link_id'])
        return redirect(url_for('links'))

@app.route("/shortener", methods=["POST", "GET"])
@login_required
def shortener():
    flash_links = []
    if request.method == "POST":

        if request.form['keyword'] == "":
            shortener = bitlyshortener.Shortener(tokens=access_tokens)
            long_urls = []
            n = request.form['shortener']
            long_urls.append(n)
            print(long_urls)
            short_url = shortener.shorten_urls(long_urls)
            for s in short_url:
                con = db.sqlite3.connect('shortener.db')
                cursor = con.cursor()
                cursor.execute("""SELECT short_link FROM user_links where short_link=? AND user_id=?;""", (s, current_user.get_id()))
                data = cursor.fetchall()
                if len(data) < 1:
                    db.create_user_link(current_user.get_id(), request.form['link_type'], request.form['shortener'], s)
                    flash_link = {}
                    flash_link["long_link"] = request.form['shortener']
                    flash_link["short_link"] = s
                    flash_links.append(flash_link)
                else:
                    flash_link = {}
                    flash_link["long_link"] = request.form['shortener']
                    flash_link["short_link"] = s
                    flash_links.append(flash_link)
        else:
            con = db.sqlite3.connect('shortener.db')
            cursor = con.cursor()
            cursor.execute("""SELECT short_link FROM user_links where long_link=? AND user_id=?;""", (request.form['shortener'], current_user.get_id()))
            data = cursor.fetchall()
            if len(data) < 1:
                keyword = request.form['keyword']
                user_short_link = "https:/j.mp/"
                user_short_link += keyword
                db.create_user_link(current_user.get_id(), request.form['link_type'], request.form['shortener'], user_short_link)
                flash_link = {}
                flash_link["long_link"] = request.form['shortener']
                flash_link["short_link"] = user_short_link
                flash_links.append(flash_link)
            else:
                keyword = request.form['keyword']
                user_short_link = "https:/j.mp/"
                user_short_link += keyword
                flash_link = {}
                flash_link["long_link"] = request.form['shortener']
                flash_link["short_link"] = user_short_link
                flash_links.append(flash_link)




    if current_user.is_authenticated:
        header_right = [{"title": "Выйти", "url": "/logout"}, {"title": "Мои ссылки", "url": "/links"}]
        return render_template('shortener.html', header_left=header_left, header_right=header_right, flash_links = flash_links)
    else:
        header_right = [{"title": "Авторизация", "url": "/login"}]
        return render_template('shortener.html', header_left=header_left, header_right=header_right, flash_links = flash_links)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(debug=True)






