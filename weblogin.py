from flask import Flask, render_template, request, url_for
from models import db, User
from forms import SignupForm
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

app.secret_key = "dev"

# Database connectiona and table
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weblogin.sqlite3'
# 'cfg['database']['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    # Extensions like Flask-SQLAlchemy now know what the "current" app
    # is while within this block. Therefore, you can now run........
    db.create_all()


@app.route('/', methods=['GET'])
def index():
    return app.config['SQLALCHEMY_DATABASE_URI']
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
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

            return email_verify_code # "success meet requirements"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
