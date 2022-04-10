import datetime
import smtplib
import sqlite3
from email.mime.text import MIMEText
from random import choice

from flask import Flask, render_template, request, make_response, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_restful import Api
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from data import db_session
from data.news import News
from data.users import User
from forms.LoginForm import LoginForm
from forms.news import NewsForm
from forms.user import RegisterForm
from resources import news_resources, users_resources
from PIL import Image


app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'SILNOVDANYA_secret_key'
mainLink = "http://127.0.0.1:5000/"
MAX_CONTENT_LENGTH = 1024 * 1024


def send_email(getter, message, subject="IRaMFan"):
    sender = "1ramfanbot@gmail.com"
    password = "987654asdvbn"
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        msg = MIMEText(message)
        msg["Subject"] = subject
        server.sendmail(sender, getter, msg.as_string())
        return "OK"
    except Exception as ex:
        return ex


def check_password(password):
    nums = "1234567890"
    if len(password) < 8:
        return "Пароль слишком короткий"
    f = False
    for i in password:
        if i not in nums:
            f = True
    if not f:
        return "Пароль содержит только числа"
    return "OK"


def generate_link():
    st = "qazwsxedcrfvtgbyhnujmikolp1234567890"
    kolvo = 12
    s = ""
    for i in range(kolvo):
        s += choice(st)
    return s


def main():
    api.add_resource(news_resources.NewsListResource, '/neriuulf7vw9da4dp316cmlq/news')
    api.add_resource(news_resources.NewsResource, '/neriuulf7vw9da4dp316cmlq/news/<int:news_id>')
    api.add_resource(users_resources.UsersListResource, '/neriuulf7vw9da4dp316cmlq/users')
    api.add_resource(users_resources.UsersResource, '/neriuulf7vw9da4dp316cmlq/users/<int:users_id>')
    db_session.global_init("db/blogs.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("ind.html", news=news)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такая почта уже есть")
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        message = check_password(form.password.data)
        if message != "OK":
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message=message)
        link = generate_link()
        send = send_email(getter=form.email.data,
                          message=f"Здравствуйте {form.name.data}. Вы зарегистрировались в IRaMFan."
                                  f"если это вы перейдите по следующей ссылке {mainLink}confirm/{link}")
        if send != "OK":
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message=send)
        user = User(
            name=form.name.data,
            email=form.email.data,
            link=link,
            authentication=False,
            admin=0,
            created_date=datetime.datetime.now())
        with open(r"C:\Users\anton\PycharmProjects\pythonNorm/static/images/defoult.png", "rb") as f:
            i = f.read()
            user.avatar = sqlite3.Binary(i)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/confirm/<link>')
def confirm(link):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.link == link).first()
    if user is None:
        return redirect("/register")
    elif user.authentication:
        return redirect("/")
    else:
        user.authentication = True
        db_sess.commit()
        return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form)


def getAvatar(appp):
    img = None
    if not current_user.avatar:
        try:
            with appp.open_resource(appp.root_path + url_for('static', filename='images/default.png'), "rb") as f:
                img = f.read()
        except FileNotFoundError as e:
            print("Не найден аватар по умолчанию: " + str(e))
    else:
        img = current_user.avatar
    return img


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.user_id == current_user.id)
    return render_template("profile.html", title="Профиль", news=news)


def verifyExt(filename):
    ver = filename.rsplit('.', 1)[1]
    if ver == "png" or ver == "PNG":
        return True
    return False


@app.route('/userava')
@login_required
def userava():
    img = getAvatar(app)
    if not img:
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        file = request.files['file']
        if file and verifyExt(file.filename):
            try:
                img = file.read()
                try:
                    binary = sqlite3.Binary(img)
                    db_sess.query(User).filter(User.id == current_user.id).first().avatar = binary
                    db_sess.commit()
                except sqlite3.Error as e:
                    print("Ошибка обновления аватара в БД: " + str(e))
                flash("Аватар обновлен")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")
    return redirect(url_for('profile'))


@app.route('/forgot')
def forgot():
    return "Нам очень жаль. что вы забыли пароль, надеемся, что в будущем мы реализуем эту функцию" \
           " и у вас будет возможность вернуть свой аккаунт!!!"


if __name__ == '__main__':
    main()
