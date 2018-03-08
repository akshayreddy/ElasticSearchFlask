
from wtforms import Form, StringField, PasswordField, validators

class Login(Form):
    username = StringField('username', [validators.Length(min=1, max=50)])
    password = PasswordField('password', [validators.Length(min=1, max=15)])


class SearchForm(Form):
    search = StringField('search')
