import os
from os import urandom
from PIL import Image

from flask import render_template, Response, request, redirect, url_for, flash, logging, session, abort
from flask_login import login_user, current_user,logout_user,login_required

from blog.forms import RegistrationForm, LoginForm, UpdateAccForm, PostForm
from blog.db_model import User, Post
from blog import app, db

from passlib.hash import sha256_crypt


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=4)
    return render_template("home.html", posts = posts)

@app.route('/about')
def about():
    return render_template("about.html", title = 'About')

@app.route('/register', methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data, password = sha256_crypt.encrypt(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash('Account created for '+ form.username.data + '!','success')
        return redirect(url_for('login'))

    return render_template("register.html", title = 'Register', form=form)

@app.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and sha256_crypt.verify(form.password.data,user.password):
            login_user(user,remember=form.remember.data)
            next_pg = request.args.get('next')
            flash('Welcome Back ! ','success')   
            if next_pg:
                return redirect(url_for('account'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Either email or password is incorrect. Please check !','danger')

    return render_template("login.html", title = 'Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_img(pic):
    random_name = urandom(8).hex()
    _,ext = os.path.splitext(pic.filename)
    img_name_root = random_name + ext
    img_path = os.path.join(app.root_path,'static/image',img_name_root)
    
    outputsize = (125,125)
    
    im = Image.open(pic)
    im.thumbnail(outputsize)
    im.save(img_path)

    return img_name_root

@app.route('/account', methods = ['GET','POST'])
@login_required
def account():
    form = UpdateAccForm()
    if form.validate_on_submit():
        if form.image.data:
            pic_file = save_img(form.image.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.image_file = pic_file
        db.session.commit()
        flash('Your account has been updated','success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='image/'+ current_user.image_file)

    return render_template('account.html',title = 'Account',image_file=image_file,form=form)

@app.route('/post/new', methods = ['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post added successfully !','success')
        return redirect(url_for('home'))

    return render_template('post_create.html',title = 'New Post',legend = 'New Post',form=form)

@app.route('/post/<int:p_id>', methods = ['GET','POST'])
def post(p_id):
    post = Post.query.get_or_404(p_id)
    return render_template('post.html', title = post.title, post=post)

@app.route('/post/<int:p_id>/update', methods = ['GET','POST'])
@login_required
def update_post(p_id):
    post = Post.query.get_or_404(p_id)
    if post.author != current_user:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated !', 'success')
        return redirect(url_for('post',p_id=post.id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('post_create.html',title = 'Update Post',legend = 'Update Post',form=form)

@app.route('/post/<int:p_id>/delete', methods = ['POST'])
@login_required
def del_post(p_id):
    post = Post.query.get_or_404(p_id)
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted !', 'success')

    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def userposts(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username = username).first_or_404()
    post_user = Post.query.filter_by(author=user)
    posts = post_user.order_by(Post.date_posted.desc()).paginate(per_page=3)
    return render_template("user.html", posts = posts, user=user)