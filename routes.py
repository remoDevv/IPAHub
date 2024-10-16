from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db, login_manager, csrf
from models import User, App, Report, Review
from forms import LoginForm, SignupForm, UploadForm, ReportForm, SearchForm, ReviewForm
from utils import allowed_file, save_file
import os
import logging
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired

main_bp = Blueprint('main', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_admin'):
            return f(*args, **kwargs)
        return abort(403)
    return decorated_function

@main_bp.route('/')
def home():
    apps = App.query.order_by(App.upload_date.desc()).limit(10).all()
    return render_template('home.html', apps=apps)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username already exists. Please choose a different username.', 'danger')
                return render_template('signup.html', form=form)

            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Email already registered. Please use a different email address.', 'danger')
                return render_template('signup.html', form=form)

            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully. You can now log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during signup: {str(e)}")
            flash('An error occurred during signup. Please try again.', 'danger')
    return render_template('signup.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            app_file = form.app_file.data
            icon_file = form.app_icon.data
            
            if not app_file:
                flash('No file part', 'danger')
                return redirect(request.url)
            
            if app_file.filename == '':
                flash('No selected file', 'danger')
                return redirect(request.url)
            
            if app_file and allowed_file(app_file.filename, ['ipa']):
                app_filename = secure_filename(app_file.filename)
                
                upload_folder = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                app_path = save_file(app_file, app_filename)
                icon_path = None
                
                if icon_file and allowed_file(icon_file.filename, ['png', 'jpg', 'jpeg']):
                    icon_filename = secure_filename(icon_file.filename)
                    icon_path = save_file(icon_file, icon_filename)
                
                new_app = App(
                    name=form.app_name.data,
                    description=form.app_description.data,
                    ios_version=form.ios_version.data,
                    file_path=app_path,
                    icon_path=icon_path,
                    user_id=current_user.id
                )
                db.session.add(new_app)
                db.session.commit()
                flash('App uploaded successfully', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Invalid file type. Only IPA files are allowed.', 'danger')
                return redirect(request.url)
        except Exception as e:
            logger.error(f"Error during file upload: {str(e)}")
            db.session.rollback()
            flash('An error occurred while uploading the file. Please try again.', 'danger')
            return redirect(request.url)
    return render_template('upload.html', form=form)

@main_bp.route('/search')
def search():
    form = SearchForm()
    query = request.args.get('query', '')
    ios_version = request.args.get('ios_version', '')
    apps = App.query
    if query:
        apps = apps.filter(App.name.ilike(f'%{query}%') | App.description.ilike(f'%{query}%'))
    if ios_version:
        apps = apps.filter(App.ios_version == ios_version)
    apps = apps.all()
    return render_template('search.html', form=form, apps=apps)

@main_bp.route('/report/<int:app_id>', methods=['GET', 'POST'])
@login_required
def report(app_id):
    app = App.query.get_or_404(app_id)
    form = ReportForm()
    if form.validate_on_submit():
        report = Report(reason=form.reason.data, app_id=app.id, user_id=current_user.id)
        db.session.add(report)
        db.session.commit()
        flash('Report submitted successfully')
        return redirect(url_for('main.home'))
    return render_template('report.html', form=form, app=app)

@main_bp.route('/admin', methods=['GET', 'POST'])
@check_admin
def admin_dashboard():
    reports = Report.query.order_by(Report.date.desc()).all()
    return render_template('admin_dashboard.html', reports=reports)

class AdminLoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@main_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        try:
            password = form.password.data
            if password == current_app.config['ADMIN_PASSWORD']:
                session['is_admin'] = True
                flash('Admin login successful', 'success')
                return redirect(url_for('main.admin_dashboard'))
            else:
                flash('Invalid admin password', 'danger')
        except Exception as e:
            logger.error(f"Error during admin login: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
    return render_template('admin_login.html', form=form)

@main_bp.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@main_bp.route('/side_loading')
def side_loading():
    return render_template('side_loading.html')

@main_bp.route('/terms')
def terms_of_service():
    return render_template('terms_of_service.html')

@main_bp.route('/privacy')
def privacy_policy():
    return render_template('privacy_policy.html')

@main_bp.route('/app/<int:app_id>', methods=['GET', 'POST'])
def app_detail(app_id):
    app = App.query.get_or_404(app_id)
    form = ReviewForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must be logged in to submit a review.', 'danger')
            return redirect(url_for('main.login'))
        review = Review(
            content=form.content.data,
            rating=form.rating.data,
            app_id=app.id,
            user_id=current_user.id
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted.', 'success')
        return redirect(url_for('main.app_detail', app_id=app.id))
    reviews = Review.query.filter_by(app_id=app.id).order_by(Review.date.desc()).all()
    return render_template('app_detail.html', app=app, form=form, reviews=reviews)

@main_bp.route('/review/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        flash('You can only edit your own reviews.', 'danger')
        return redirect(url_for('main.app_detail', app_id=review.app_id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review.content = form.content.data
        review.rating = form.rating.data
        db.session.commit()
        flash('Your review has been updated.', 'success')
        return redirect(url_for('main.app_detail', app_id=review.app_id))
    elif request.method == 'GET':
        form.content.data = review.content
        form.rating.data = review.rating
    
    return render_template('edit_review.html', form=form, review=review)

@main_bp.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id:
        flash('You can only delete your own reviews.', 'danger')
        return redirect(url_for('main.app_detail', app_id=review.app_id))
    
    db.session.delete(review)
    db.session.commit()
    flash('Your review has been deleted.', 'success')
    return redirect(url_for('main.app_detail', app_id=review.app_id))