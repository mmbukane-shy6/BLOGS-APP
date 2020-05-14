import os
import secrets
from flask import render_template, url_for, flash, redirect, abort,request
from . import main
# from .. import bcrypt
from .forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentsForm
from ..models import User, Post, Comment,db
from flask_login import login_user, current_user, logout_user, login_required
from ..request import get_quote
from app import bcrypt



@main.route("/")
def home():
    posts = Post.query.all()
    quote = get_quote()       
    return render_template('index.html', posts=posts, quote=quote)

@main.route("/register", methods=['GET','POST'])

def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    quote=get_quote()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data , email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Account created!, please log in','success')
        return redirect (url_for('main.login'))

    return render_template('register.html', title='Register', form=form,quote=quote)

@main.route("/login",methods=['GET','POST'])

def login():
    quote=get_quote()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email = login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
        # if user and user.password(user.password, form.password.data):
        # if user is not None: 
        # and user.verify_password(login_form.password.data):
            login_user(user,remember=login_form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', login_form = login_form,quote=quote)

@main.route("/logout")
def logout():
    quote=get_quote()
    logout_user()
    return redirect(url_for('main.home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images',picture_fn)
    form_picture.save(picture_path)

    return picture_fn


@main.route("/account", methods=['GET','POST'])
@login_required
def account():
    quote=get_quote()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account Updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET' :
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file = image_file , form = form,quote=quote)


@main.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    form= PostForm()
    quote=get_quote()
    if form.validate_on_submit():
        post = Post(title = form.title.data,content = form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html',title='New post', form=form,quote=quote)


@main.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    quote = get_quote()
    return render_template('post.html' , title=post.title, post=post, quote=quote)

@main.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    quote=get_quote()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('main.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post',quote=quote)

@main.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    
    post = Post.query.get(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted!', 'success')
    return redirect(url_for('main.home'))

@main.route("/post/<int:post_id>/comments")
def comments(post_id):
    form = CommentsForm()
    quote=get_quote()
    post = Post.query.get(post_id)
    comment = Comment.get_comments(post_id)
    return render_template('comments.html',post_id=post_id, comment = comment,comment_form=form, quote=quote)

@main.route('/post/<int:post_id>/comments/new', methods=["GET", "POST"])
@login_required
def comment(post_id):
    '''
    view function that return a form to comment on a given post
    '''
    form = CommentsForm()
    quote=get_quote()
    post = Post.query.get(post_id)
    if form.validate_on_submit():
        comment = form.comment.data
        new_comment = Comment( post_id=post_id, comment_post=comment, user_id=current_user.id)
        db.session.add(new_comment)
        print(current_user.id,'================================')
        db.session.commit()
        # new_comment.save_comments()
        return redirect(url_for('main.comments', post_id=post_id))
    
    return render_template('new_comment.html',comment_form=form, post=post,quote=quote)

    