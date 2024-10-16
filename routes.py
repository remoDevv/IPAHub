from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db, login_manager
from models import User, App, Report
from forms import LoginForm, SignupForm, UploadForm, ReportForm, SearchForm
from utils import allowed_file, save_file
import os

main_bp = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully')
        return redirect(url_for('main.login'))
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
        app_file = form.app_file.data
        icon_file = form.app_icon.data
        if app_file and allowed_file(app_file.filename, ['ipa']):
            app_filename = secure_filename(app_file.filename)
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
            flash('App uploaded successfully')
            return redirect(url_for('main.home'))
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

@main_bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    reports = Report.query.order_by(Report.date.desc()).all()
    return render_template('admin_dashboard.html', reports=reports)

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
