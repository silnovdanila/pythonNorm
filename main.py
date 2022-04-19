import datetime
import os
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
from forms import confirmForm
from forms.AdminForm import AdminForm
from forms.LoginForm import LoginForm
from forms.news import NewsForm, NewsUpdate
from forms.user import RegisterForm
from resources import news_resources, users_resources

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'SILNOVDANYA_secret_key'
app.config["SQLALCHEMY_ECHO"] = True
mainLink = "https://whispering-hollows-34027.herokuapp.com/"
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # waitress.serve(app, host="0.0.0.0", port=5000)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private is not True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private is not True))
    else:
        news = db_sess.query(News).filter(News.is_private is not True)
    news = sorted(news, key=lambda x: x.created_date, reverse=True)
    return render_template("ind.html", news=news, title="Новости")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такая почта уже есть")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Это имя уже занято")
        if len(form.name.data) < 5:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Имя слишком короткое")
        if form.name.data[-5:] == "admin":
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Уберите admin с конца имени!!!")
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
            created_date=datetime.datetime.now(),
            banned=False)
        with open(mainLink + url_for('static', filename='defoult.png'), "rb") as f:
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


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    if not current_user.banned:
        form = NewsUpdate()
        image = None
        new = None
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            news = db_sess.query(News).filter(News.id == id
                                              ).first()
            if news:
                if current_user.id == news.user_id or current_user.admin != 0:
                    news.title = form.title.data
                    news.content = form.content.data
                    file = request.files['file']
                    if file and verifyExt(file.filename) and file is not None:
                        img = file.read()
                        binary = sqlite3.Binary(img)
                        news.img = binary
                    news.is_private = form.is_private.data
                    db_sess.commit()
                    return redirect('/')
            else:
                abort(404)
        if request.method == "GET":
            db_sess = db_session.create_session()
            news = db_sess.query(News).filter(News.id == id
                                              ).first()
            if news:
                if current_user.id == news.user_id or current_user.admin != 0:
                    form.title.data = news.title
                    form.content.data = news.content
                    form.is_private.data = news.is_private
                    new = news.id
                    if news.img is not None:
                        image = news.img
            else:
                abort(404)

        return render_template('news.html',
                               title='Редактирование новости',
                               form=form, image=image, new=new)
    else:
        return make_response("Ахахаха чел ты в бане")


@app.route("/news/newsimage/<int:id>")
@login_required
def newsimage(id):
    if not current_user.banned:
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id).first()
        image = "1"
        if news is not None:
            img = news.img
            if img is not None:
                image = img

        db_sess.commit()
        return image
    else:
        return make_response("Ахахаха чел ты в бане")


def getAvatar(appp, id):
    img = None
    db_sess = db_session.create_session()
    uesr = db_sess.query(User).filter(User.id == id
                                      ).first()
    if not uesr.avatar:
        try:
            with appp.open_resource(appp.root_path + url_for('static', filename='images/defoult.png'), "rb") as f:
                img = f.read()
        except FileNotFoundError as e:
            print("Не найден аватар по умолчанию: " + str(e))
    else:
        img = uesr.avatar
    return img


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    if not current_user.banned:
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id
                                          ).first()
        if news:
            if news.user_id == current_user.id or current_user.admin != 0:
                db_sess.delete(news)
                db_sess.commit()
        else:
            abort(404)
        return redirect('/')
    else:
        return make_response("Ахахаха чел ты в бане")


@app.route('/users/<int:id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    if not current_user.banned:
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.user_id == id)

        user = db_sess.query(User).filter(User.id == id).first()
        if user is not None:
            return render_template("profile.html", title="Профиль", news=news, user=user)
        else:
            return make_response("Такого пользователя не существует, вы зашли не на тот сайт бейби.")
    else:
        return make_response("Чееееееел, когда ты в бане на пользователей не посмотришь")


def verifyExt(filename):
    ver = filename.rsplit('.', 1)[1]
    if ver == "png" or ver == "PNG":
        return True
    return False


@app.route('/users/userava/<int:id>')
def userava(id):
    img = getAvatar(app, id)

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
    return redirect(url_for("profile", id=current_user.id))


@app.route('/forgot')
def forgot():
    return "Нам очень жаль. что вы забыли пароль, надеемся, что в будущем мы реализуем эту функцию" \
           " и у вас будет возможность вернуть свой аккаунт!!!"


@app.route("/add_image", methods=["POST", "GET"])
@login_required
def add_image():
    if request.method == 'POST':
        pass
    return redirect(url_for('news'))


@app.route("/delete_image")
@login_required
def delete_image():
    pass


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    if not current_user.banned:
        form = NewsForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            news = News()
            news.title = form.title.data
            news.content = form.content.data
            file = request.files['file']
            if file is not None:
                if file and verifyExt(file.filename):
                    try:
                        img = file.read()
                        try:
                            binary = sqlite3.Binary(img)
                            news.img = binary
                        except sqlite3.Error as e:
                            print("Ошибка добавления фото: " + str(e))
                        flash("Фото добавлено")

                    except FileNotFoundError as e:
                        flash("Ошибка чтения файла", "error")
            news.is_private = form.is_private.data
            current_user.news.append(news)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        return render_template('news.html', title='Добавление новости',
                               form=form)
    else:
        return make_response("Ахахаха чел ты в бане")


@app.route("/for_real_connoisseurs")
@login_required
def nyancat():
    if not current_user.banned:
        visits_count = int(request.cookies.get("visits_count", 0))
        cats = ["https://upload.wikimedia.org/wikipedia/ru/6/6b/NyanCat.gif",
                "https://c.tenor.com/v9sdELSzVw4AAAAM/nyan-cat-kawaii.gif",
                "https://c.tenor.com/ZAFeUhHd7wUAAAAM/cat-nyan-cat.gif",
                "https://c.tenor.com/0jI-YXeywSsAAAAM/nyan-cat-cat.gif",
                "https://thumbs.gfycat.com/AnimatedMedicalHorseshoebat-size_restricted.gif",
                "https://i.pinimg.com/originals/7a/1c/f0/7a1cf0680ae666cac23cf65387a641a1.gif",
                "https://i.pinimg.com/originals/bb/40/c1/bb40c15cde81c0a1cf9a218c1527fc76.gif",
                "https://99px.ru/sstorage/56/2014/09/13009141434028416.gif",
                "https://lh3.googleusercontent.com/pfRjRVITeeQs3OBvhnDUU8Us6eV57bbr5AoAbb57J0qn52cKKndMe2prIswKX_u48slpha66UWGoe_8GZj94l1JFGP7vAFHzRN7u=w600",
                "https://99px.ru/sstorage/86/2017/09/image_86060917012425311405.gif",
                "https://pa1.narvii.com/5860/2819aa5af85fafd8fc6d781e75d061fc4275fce8_hq.gif",
                "https://64.media.tumblr.com/c65aa86f3c7ac8d278aaa4321562a1e5/tumblr_nx04ydQkqY1udh5n8o1_500.gifv",
                "https://thumbs.gfycat.com/BigheartedFavoriteCrocodileskink-size_restricted.gif",
                "https://ipfs.nftndx.io/ipfs/QmS7xpFLWDXNVZyTpfrSsQwDu6BA73fJnizLcA5LfJLgKM/image.gif"]
        if visits_count:
            if visits_count < 15:
                zvanie = "Noviy cat"
            elif visits_count < 50:
                zvanie = "Cat master"
            elif visits_count < 200:
                zvanie = "Cat General"
            elif visits_count <= 1000:
                zvanie = "Тебе нечем заняться"
            else:
                zvanie = "Кто ты такой и откуда у тебя столько свободного\n времени??? Ты мне сайт сломаешь!!!"
            message = f"Вы зашли на эту страницу {visits_count + 1} раз\n" \
                      f"Ваше звание '{zvanie}'"
            res = make_response(render_template("nyanCat.html", message=message, gif=choice(cats)))
            res.set_cookie("visits_count", str(visits_count + 1),
                           max_age=60 * 60 * 24 * 2)
        else:
            res = make_response(
                "Вы здесь впервые, позвольте вас познакомить с небольшим Клубом любителей Nyan cat."
                "Обновляйте страницу и получайте звание. Удачи!!!")
            res.set_cookie("visits_count", '1',
                           max_age=60 * 60 * 24 * 2)
        return res
    else:
        return make_response("Чел ты вычеркнут из клуба")


@app.route("/admin_if_you_admin", methods=['GET', 'POST'])
@login_required
def admin_panel():
    if current_user.admin != 0:
        form = AdminForm()
        if form.validate_on_submit() or request.method == 'POST':
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == form.user_id.data).first()
            if user is None:
                return render_template("admin.html", form=form, message="Такой id не зарегистрирован")
            else:
                return redirect(f"/r_u_sure_ban/{user.id}")
        return render_template("admin.html", form=form)
    else:
        return make_response("Ты даже не админ, тебе здесь делать нечего!!!")


@app.route("/r_u_sure_ban/<int:bid>", methods=['GET', 'POST'])
@login_required
def ban(bid):
    if current_user.admin != 0:
        if not current_user.banned:
            form = confirmForm.AdminForm()
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == bid).first()
            if user is None:
                return make_response("Нету такого юзера")
            else:
                if int(current_user.admin) > int(user.admin):
                    if request.method == "POST":
                        user.banned = True
                        return redirect("/")
                    return render_template("r_u_sure_ban.html", form=form, id=bid, name=user.name)
                else:
                    return make_response("Ахахахаха ты слишком слабый Админ")
        else:
            return make_response("Офигеть админ и в бане, как это случилось?")
    else:
        return make_response("Ты даже не админ, тебе здесь делать нечего!!!")


@app.route("/see_news/<int:sid>")
@login_required
def see_news(sid):
    if not current_user.banned:
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == sid).first()
        image = None
        if news.img:
            image = True
        return render_template("see_news.html", news=news, image=image)
    else:
        return make_response("АХАХАХ чеел ты в ьане")


if __name__ == '__main__':
    main()
