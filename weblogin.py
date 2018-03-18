from flask import Flask, render_template, request, url_for, session, redirect
from flask_mail import Mail, Message
from urllib import parse
from models import db, User, system_settings
from forms import SignupForm, LoginForm
import configparser
from os import path
import uuid

cfg = configparser.ConfigParser()
# Check if config.ini file exist before loading
if path.isfile('config.ini'):
    cfg.read('config.ini')
else:
    print('No config.ini file found')
    exit(1)


app = Flask(__name__)

app.secret_key = "Development Key"

# Database connectiona and table
app.config['SQLALCHEMY_DATABASE_URI'] = \
    cfg['database']['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    # Extensions like Flask-SQLAlchemy now know what the "current" app
    # is while within this block. Therefore, you can now run........
    db.create_all()


# Mailer
mail = Mail(app)

app.config.update(
    DEBUG=True,
    MAIL_SERVER=cfg['mail']['MAIL_SERVER'],
    MAIL_PORT=cfg['mail']['MAIL_PORT'],
    MAIL_USE_SSL=True,
    MAIL_USERNAME=cfg['mail']['MAIL_USERNAME'],
    MAIL_PASSWORD=cfg['mail']['MAIL_PASSWORD']
)

mail = Mail(app)


def emailuser(email, confirmurl):

    msg = Message(subject="FlaskLogin confirm registation",
                  sender="Register@flasklogin.com",
                  recipients=[email])
    msg.html = "<!DOCTYPE html>"
    msg.html += "<h2>Weblogin - please confirm email address</h2>"
    msg.html += "<div>Click on the link to activate the your account.</div>"
    msg.html += "<div><a href=\"" + confirmurl + "\">Activate account</a><div>"
    mail.send(msg)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    if 'email' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')


@app.route('/logoff')
def logoff():
    if 'email' in session:
        session.pop('email')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('login.html', form=form)
        else:
            email = form.email.data
            password = form.password.data

            user = User.query.filter_by(email=email).first()
            if user is None:
                return redirect(url_for('login', id='failed'))
            # Check if account has been verified
            if not user.account_verified:
                return redirect(url_for('login', id='emailnotverified'))

            # Check password
            if user is not None and user.check_password(password):
                session['email'] = email
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login', id='failed'))

    elif request.method == 'GET':
        id = request.args.get('id')

        return render_template('login.html', form=form, id=id)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if cfg['system_settings']['disable_signup'] == "True":
        return redirect(url_for('index'))

    form = SignupForm()
    if request.method == 'GET':
        return render_template('signup.html', form=form)
    elif request.method == 'POST':
        if not form.validate():
            return render_template('signup.html', form=form)
        else:
            email_verify_code = str(uuid.uuid1())
            newuser = User(form.first_name.data,
                           form.last_name.data,
                           form.email.data,
                           form.password.data,
                           False,
                           email_verify_code,
                           False)
            db.session.add(newuser)
            db.session.commit()

            confirmurl = "http://localhost/" + \
                parse.quote(form.email.data) + "/" + email_verify_code

            emailuser(form.email.data, confirmurl)

            # "success meet requirements"
            return redirect(url_for('login', id='emailsent'))


@app.route('/<email>/<email_verify_code>')
def authcheck(email, email_verify_code):

    user = User.query.filter_by(email=email).first()
    if user is None:
        return redirect(url_for('index'))

    if user.email_verify_code == email_verify_code:
        user.account_verified = True
        db.session.commit()
        # return render_template(url_for('login'))
        return redirect(url_for('login'))

    else:
        return ('sadly it doesn\'t match')

    return ("email {} \br authcode {}".format(email, email_verify_code))


if __name__ == '__main__':
    # with app.app_context():
    #     system = system_settings.query.filter_by(disable_signup=False).first()
    #     if system is None:
    #         system = system_settings(website_name='Demo',disable_signup=False)
    #         db.session.add(system)
    #         db.session.commit()
    #     else:
    #         disbale_signup = system.disable_signup
        # user = User.query.filter_by(email="hh").first()
    app.run(host='0.0.0.0', debug=True)
