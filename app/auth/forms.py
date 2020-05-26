from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, ValidationError
)
from wtforms.validators import (
    Required, Email, Length, Regexp, EqualTo
)
from ..models import User
from flask_login import current_user


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        Required(), Length(1, 64), Email()
    ])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Email does not registered.')
    
    def validate_password(self, field):
        user = User.query.filter_by(email=self.email.data).first()
        if user and not user.verify_password(field.data):
            raise ValidationError('Invalid password.')


class RegistrationForm(FlaskForm):
    firstname = StringField('First name', validators=[Required()])
    lastname = StringField('Last name', validators=[Required()])
    email = StringField('Email', validators=[
        Required(), Length(1, 64), Email()
    ])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[a-zA-Z0-9][a-zA-Z0-9_.]*$', 0,
                                          'Username must have only letters, '
                                          'numbers, dot or underscores.')
    ])
    password = PasswordField('Password', validators=[
        Required(), Length(8),
        EqualTo('password', message='Password must match.')
    ])
    password2 = PasswordField('Confirm Password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')
    
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[
        Required(), Length(8),
        EqualTo('password2', message='New password must match.')
    ])
    password2 = PasswordField('Confirm new password', validators=[
        Required()
    ])
    submit = SubmitField('Update Password')

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('Invalid password.')
    
    def validate_password(self, field):
        if field.data == self.old_password.data:
            raise ValidationError('New password must change.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Email()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email does not registered.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password', validators=[
        Required(), Length(8),
        EqualTo('password2', message='Password must match.')
    ])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')


class ChangeEmailForm(FlaskForm):
    password = PasswordField('Password', validators=[Required()])
    email = StringField('New email', validators=[Required(), Email()])
    submit = SubmitField('Update Email')

    def validate_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('Invalid password.')
    
    def validate_email(self, field):
        if field.data == current_user.email:
            raise ValidationError('Email must change.')
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email has been registered.')
