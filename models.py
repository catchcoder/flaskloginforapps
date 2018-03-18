from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column('username_id',
                    db.Integer,
                    primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120),
                      unique=True)
    password_hash = db.Column(db.String(200))
    account_verified = db.Column(db.Boolean,
                                 nullable=False,
                                 default=False)
    email_verify_code = db.Column(db.String(36))
    is_admin = db.Column(db.Boolean,
                         nullable=False,
                         default=False)

    def __init__(self,
                 first_name,
                 last_name,
                 email,
                 password_hash,
                 account_verified,
                 email_verify_code,
                 is_admin):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email.lower()
        self.set_password(password_hash)
        self.account_verified = account_verified
        self.email_verify_code = email_verify_code
        self.is_admin = is_admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_verified(self):
        return self.account_verified


class system_settings(db.Model):
    __tablename__ = 'system'
    sid = db.Column(db.Integer, primary_key=True)
    website_name = db.Column(db.String(200))
    disable_signup = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, website_name, disable_signup):
        self.website_name = website_name
        self.disable_signup = disable_signup

    def check_sign_available(self):
        return self.disable_signup
