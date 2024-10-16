import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from app import db, login_manager
from models import User, IPAApp, Review, Download
from forms import SignupForm, LoginForm, UploadForm, SearchForm, ReviewForm
from utils import admin_required, allowed_file

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main_bp.route('/')
def index():
    featured_apps = IPAApp.query.order_by(IPAApp.id.desc()).limit(6).all()
    return render_template('index.html', featured_apps=featured_apps)

@main_bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data
        apps = IPAApp.query.filter(IPAApp.name.contains(query) | IPAApp.description.contains(query)).all()
        return render_template('search.html', form=form, apps=apps)
    return render_template('search.html', form=form)

@main_bp.route('/tutorials')
def tutorials():
    return render_template('tutorials.html')

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        icon_filename = secure_filename(form.icon.data.filename)
        ipa_filename = secure_filename(form.ipa_file.data.filename)

        icon_path = os.path.join('uploads', 'icons', icon_filename)
        ipa_path = os.path.join('uploads', 'ipas', ipa_filename)

        form.icon.data.save(icon_path)
        form.ipa_file.data.save(ipa_path)

        new_app = IPAApp()  # Create the object without any arguments
        new_app.name = form.name.data
        new_app.description = form.description.data
        new_app.compatibility = form.compatibility.data
        new_app.icon_path = icon_path
        new_app.file_path = ipa_path
        new_app.user_id = current_user.id
        db.session.add(new_app)
        db.session.commit()

        flash('IPA app uploaded successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('upload.html', form=form)

@admin_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    apps = IPAApp.query.all()
    return render_template('admin.html', users=users, apps=apps)

@main_bp.route('/download/<int:app_id>')
@login_required
def download_app(app_id):
    app = IPAApp.query.get_or_404(app_id)
    download = Download(user_id=current_user.id, app_id=app.id)
    db.session.add(download)
    db.session.commit()
    return send_from_directory(os.path.dirname(app.file_path), os.path.basename(app.file_path), as_attachment=True)

@main_bp.route('/app/<int:app_id>', methods=['GET', 'POST'])
@login_required
def app_details(app_id):
    app = IPAApp.query.get_or_404(app_id)
    form = ReviewForm()
    if form.validate_on_submit():
        existing_review = Review.query.filter_by(user_id=current_user.id, app_id=app.id).first()
        if existing_review:
            existing_review.content = form.content.data
            existing_review.rating = form.rating.data
            flash('Your review has been updated!', 'success')
        else:
            review = Review(
                content=form.content.data,
                rating=form.rating.data,
                user_id=current_user.id,
                app_id=app.id
            )
            db.session.add(review)
            flash('Your review has been submitted!', 'success')
        db.session.commit()
        return redirect(url_for('main.app_details', app_id=app.id))
    reviews = Review.query.filter_by(app_id=app.id).order_by(Review.timestamp.desc()).all()
    return render_template('app_details.html', app=app, form=form, reviews=reviews)

@auth_bp.route('/profile')
@login_required
def profile():
    downloads = Download.query.filter_by(user_id=current_user.id).order_by(Download.timestamp.desc()).all()
    return render_template('profile.html', user=current_user, downloads=downloads)

@main_bp.route('/favorite/<int:app_id>', methods=['POST'])
@login_required
def favorite_app(app_id):
    app = IPAApp.query.get_or_404(app_id)
    if app in current_user.favorites:
        current_user.favorites.remove(app)
        flash('App removed from favorites.', 'success')
    else:
        current_user.favorites.append(app)
        flash('App added to favorites.', 'success')
    db.session.commit()
    return redirect(url_for('main.app_details', app_id=app_id))