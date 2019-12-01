from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import Form, StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from blog.db_model import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[Length(min=4,max=25),DataRequired()],render_kw={"placeholder":"abc123"})
    email = StringField('Email',validators=[DataRequired(),Email()],render_kw={"placeholder":"jb@xyz.com"})
    password = PasswordField('Password',validators=[DataRequired()])
    confirm = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password', message="Passwords do not match")])
    submit = SubmitField('Sign Up')

    def user_validation(self,username):
        user = User.query.filter_by(username.data).first()
        if user:
            raise ValidationError('The Username is taken. Please use other name.')

    def email_validation(self,email):
        email = User.query.filter_by(email.data).first()
        if email:
            raise ValidationError('The Email is taken. Please use other mail id.')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()],render_kw={"placeholder":"jb@xyz.com"})
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccForm(FlaskForm):
    username = StringField('Username',validators=[Length(min=4,max=25),DataRequired()],render_kw={"placeholder":"abc123"})
    email = StringField('Email',validators=[DataRequired(),Email()],render_kw={"placeholder":"jb@xyz.com"})
    image = FileField('Update Profile Pic',validators=[FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Update')

    def user_validation(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username.data).first()
            if user:
                raise ValidationError('The Username is taken. Please use other name.')

    def email_validation(self,email):
        if username.data != current_user.username:
            email = User.query.filter_by(email.data).first()
            if email:
                raise ValidationError('The Email is taken. Please use other mail id.')

class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()],render_kw={"placeholder":"Enter your blog title"})
    content = TextAreaField('Content',validators=[DataRequired()])
    submit = SubmitField('Post')
