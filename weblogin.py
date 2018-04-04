#!/usr/bin/env python
"""
title           :weblogin.py
description     :Frontend for other web app that need securing.
author          :Chris Hawkins
date            :20180318
version         :0.8
usage           :python weblogin.py
notes           :Need to run pip install -r requirements.txt
python_version  :3.5+
============================================ ==================================
"""

# Import the modules needed to run the script.
import configparser
import uuid
import RPi.GPIO as GPIO
from functools import wraps
from os import path
from urllib import parse
from flask import Flask, render_template, request, url_for, session, redirect
from flask_mail import Mail, Message

from forms import SignupForm, LoginForm
app = Flask(__name__)

app.secret_key = "Development Key"
from models import db, User, system_settings


# Load setting and passwords from config.ini
# config.ini.example if provided, rename and edit
CFG = configparser.ConfigParser()
# Check if config.ini file exist before loading
if path.isfile('config.ini'):
    CFG.read('config.ini')
else:
    print('No config.ini file found')
    exit(1)



# Database connectiona and table
app.config['SQLALCHEMY_DATABASE_URI'] = \
    CFG['database']['SQLALCHEMY_DATABASE_URI']
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
    MAIL_SERVER=CFG['mail']['MAIL_SERVER'],
    MAIL_PORT=CFG['mail']['MAIL_PORT'],
    MAIL_USE_SSL=True,
    MAIL_USERNAME=CFG['mail']['MAIL_USERNAME'],
    MAIL_PASSWORD=CFG['mail']['MAIL_PASSWORD']
)

mail = Mail(app)
##############################################################





##############################################################


def emailuser(email, confirm_url, first_name):

    msg = Message(subject="Login confirm registration",
                  sender="Register@flasklogin.com",
                  recipients=[email])
    msg.html = render_template(url_for('email.html'),first_name, confirm_url)
    # msg.html = "<!DOCTYPE html>"
    # msg.html += "<h2>Weblogin - please confirm email address</h2>"
    # msg.html += "<div>Click on the link to activate the your account.</div>"
    # msg.html += "<div><a href=\"" + confirm_url + "\">Activate account</a><div>"
    mail.send(msg)


def check_login(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('index'))

        return func(*args, **kwargs)

    return func_wrapper


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/home')
@check_login
def home():
    return render_template('home.html', gpio_pin_state=gpio_pin_state)




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
            email = form.email.data.lower().strip()
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
                return redirect(url_for('webapp'))
            else:
                return redirect(url_for('login', id='failed'))

    elif request.method == 'GET':
        id = request.args.get('id')

        return render_template('login.html', form=form, id=id)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if CFG['system_settings']['disable_signup'] == "True":
        return redirect(url_for('index'))

    form = SignupForm()
    if request.method == 'GET':
        return render_template('signup.html', form=form)
    elif request.method == 'POST':
        if not form.validate():
            return render_template('signup.html', form=form)
        else:
            email_verify_code = str(uuid.uuid1())
            first_name = form.first_name.data.title().strip()
            password =form.password.data
            newuser = User(first_name,
                           form.last_name.data.title.strip(),
                           form.email.data.lower().strip(),
                           password,
                           False,
                           email_verify_code,
                           False)
            db.session.add(newuser)
            db.session.commit()

            confirmurl = "http://localhost:5000/" + \
                parse.quote(form.email.data) + "/" + email_verify_code

            emailuser(password, confirmurl, first_name)

            # "success meet requirements"
            return redirect(url_for('login', id='emailsent'))


@app.route('/<email>/<email_verify_code>')
def authcheck(email, email_verify_code):

    user = User.query.filter_by(email=email).first()
    if user is None:
        return redirect(url_for('index'))

    if user.email_verify_code == email_verify_code:
        user.account_verified = True
        user.email_verify_code = ""
        db.session.commit()
        # return render_template(url_for('login'))
        return redirect(url_for('login'))

    else:
        return 'sadly it doesn\'t match'

    return "email {} \br authcode {}".format(email, email_verify_code)

########################## Put code here #############################

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


GPIO_PINS = [17, 27, 22, 10, 9, 11, 5, 6, 13]
gpio_pin_state = {}


def setup_outputs():
    """ Setup GPIOs for outputs.
    """
    for pin in GPIO_PINS:
        GPIO.setup(pin, GPIO.OUT)


setup_outputs()

GPIO.setup(2, GPIO.OUT)
GPIO.output(2, False)

gpio_path = "/sys/class/gpio/gpio{}/value"
# gpio_path = "/home/chris/repos/flaskapp/value"


def check_gpio_state(pin):
    """ Read value file (one character) for either 0 or a 1
    """
    try:
        with open(gpio_path.format(pin)) as gpiopin:
            status = gpiopin.read(1)
    except Exception:
        status = 0

    return True if status == "1" else False


def check_all_gpios():
    """ reload dictionary of GPIO's statues T or F
    """
    global gpio_pin_state
    gpio_pin_state = {}

    for pin in GPIO_PINS:
        gpio_pin_state[pin] = check_gpio_state(pin)


def allonoroff(state):
    """ Set all GPIOs dictionary to either T or F
    """
    for pin in GPIO_PINS:
        GPIO.output(pin, state)


def swap_states():
    """ flip state of all GPIO's to their opposite state
    """
    for pin in GPIO_PINS:
        GPIO.output(pin, not check_gpio_state(pin))






@app.route('/webapp')
@check_login
def webapp():
    # eturn redirect(url_for('index'))
    check_all_gpios()
    return render_template('home.html', gpio_pin_state=gpio_pin_state)

@app.route('/gpioon/<int:gpio_pin>')
@check_login
def gpioon(gpio_pin):
    if gpio_pin in GPIO_PINS:
        GPIO.output(gpio_pin, True)
    return redirect(url_for('webapp'))


@app.route('/gpiooff/<int:gpio_pin>')
@check_login
def gpiooff(gpio_pin):
    if gpio_pin in GPIO_PINS:
        GPIO.output(gpio_pin, False)
    return redirect(url_for('webapp'))


@app.route('/switch')
@check_login
def switch():
    swap_states()
    return redirect(url_for('webapp'))


@app.route('/all/<state>')
@check_login
def all(state):
    if state == "off":
        allonoroff(False)
    else:
        allonoroff(True)
    return redirect(url_for('webapp'))


######################### End code here ##############################

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
