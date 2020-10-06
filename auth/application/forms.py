from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')


class NewUserForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    username = StringField('Usuario', validators=[DataRequired()])
    password1 = PasswordField(
        'Contraseña', validators=[DataRequired(), EqualTo('password2')])
    password2 = PasswordField('Confirmar Contraseña')
    next = HiddenField()
