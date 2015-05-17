__author__ = 'mg'
from wtforms.form import Form
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp
import re


class LoginForm(Form):
    login = StringField('login', validators = [Length(min=6, max=80),
                                               Regexp(re.compile('^(_*[A-Za-z]*[0-9]*)*$'), 0, 'Latina')])
    password=PasswordField('password', validators = [Length(min=8)])
    remember_me = BooleanField('remember_me', default = True)
