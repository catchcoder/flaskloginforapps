from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class SignupForm(FlaskForm):
    first_name = StringField('First name', validators=[
                             DataRequired("Please enter your first name.")])
    last_name = StringField('Last name', validators=[
                            DataRequired("Please enter your last name.")])
    email = StringField('Email address', validators=[DataRequired(
        "Please enter your email address."),
        Email("Please enter a valid email address.")])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired(
                                     "Please enter your Password."),
                                 Length(
                                     min=8,
                                     message="Passwords must be 8 characters or more."),
                                 EqualTo(
                                     'confirm',
                                     message='Passwords must match')])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(
        "Please confirm your Password."), Length(min=8,
                                                 message="")])
    submit = SubmitField('Sign up', validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(
        "Please enter your email address."),
        Email("Please enter a valid email address.")])
    password = PasswordField(
        'Password',
        validators=[DataRequired("Please enter your Password."),
                    Length(
                        min=8,
                        message="Passwords must be 8 characters or more.")])
    submit = SubmitField('Login', validators=[DataRequired()])
