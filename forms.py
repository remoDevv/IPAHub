from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class UploadForm(FlaskForm):
    app_name = StringField('App Name', validators=[DataRequired()])
    app_description = TextAreaField('App Description', validators=[DataRequired()])
    ios_version = StringField('iOS Version Compatibility', validators=[DataRequired()])
    app_file = FileField('IPA File', validators=[DataRequired()])
    app_icon = FileField('App Icon')
    submit = SubmitField('Upload')

class ReportForm(FlaskForm):
    reason = TextAreaField('Reason for Report', validators=[DataRequired()])
    submit = SubmitField('Submit Report')

class SearchForm(FlaskForm):
    query = StringField('Search')
    ios_version = StringField('iOS Version')
    submit = SubmitField('Search')

class ReviewForm(FlaskForm):
    content = TextAreaField('Review', validators=[DataRequired(), Length(min=10, max=500)])
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Submit Review')
