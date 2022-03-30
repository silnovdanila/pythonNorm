from flask import Flask, render_template
# from flask_login import LoginManager
from werkzeug.utils import redirect

from data import db_session
from data.news import News
from data.users import User
from forms.user import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
"""login_manager = LoginManager()
login_manager.init_app(app)
"""


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


def main():
    db_session.global_init("db/blogs.db")
    app.run()


"""@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)"""


@app.route("/")
def index():
    db_sess = db_session.create_session()
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
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    main()
