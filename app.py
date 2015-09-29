from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from functools import wraps
import os
from werkzeug import secure_filename
from flask_mail import Mail, Message



POSTS_PER_PAGE=1
POSTS_PER_PAGE_ADMIN=2


#config
app = Flask(__name__)
bcrypt = Bcrypt(app)
DEBUG = False
app.secret_key = "IT'S A SECRET"


app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://username:password@databaseurl/databasename'


# create the sqlalchemy object
db = SQLAlchemy(app)

import models
from models import *


# mail config
mail = Mail()
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'superyaooo@gmail.com'
app.config["MAIL_PASSWORD"] = 'SECRET PASSWORD'

mail.init_app(app)



app.config['UPLOAD_FOLDER'] = 'brokentoystory/static/img'

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif','PNG','JPG','JPEG','GIF'])





#login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    query = models.BlogPost.query.order_by(BlogPost.id.desc())
    posts = query.paginate(page, POSTS_PER_PAGE, False)
    counts = db.session.query(BlogPost).count()

    if page > counts:
        return redirect(url_for('error'))
    else:
        if request.method == 'POST':
            msg = Message('New message from BrokenToyStory', sender='superyaooo@gmail.com', recipients=['superyaooo@gmail.com'])
            msg.body = """
            From: %s <%s>
            %s
            """ % (request.form['name'], request.form['email'], request.form['message'])

            if not request.form['name']:
                flash('Your name cannot be empty in the message form. Please try again.')
            elif not request.form['message']:
                flash('Message area cannot be empty in the message form. Please try again.')
            elif not request.form['email']:
                flash('Email cannot be empty in the message form. Please try again.')
            else:
                mail.send(msg)
                flash('Thank you for your message. I\'ll get back to you soon.')
                return redirect(url_for('index'))


        return render_template('index.html', posts=posts)


@app.route('/post/<int:id>', methods=['GET','POST'])
def post(id):
    post = db.session.query(BlogPost).get(id)

    if post == None:
        return redirect(url_for('error'))
    else:
        return render_template('post.html', post=post)



@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html')



@app.route('/admin', methods=['GET','POST'])
@app.route('/admin/<int:page>', methods=['GET','POST'])
@login_required
def admin(page=1):
    if request.method =='POST':
        file=request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        elif file and not allowed_file(file.filename):
            flash('Only pictures are allowed to be uploaded!')
            return redirect(url_for('admin'))

        elif not file:
            flash('Must upload a picture!')
            return redirect(url_for('admin'))


        new_post=BlogPost(
            request.form['title'],
            '/static/img/'+ filename,
            request.form['content']
        )
        db.session.add(new_post)
        db.session.commit()
        flash('New entry was successfully posted.')
        return redirect(url_for('admin'))
    else:
        query = models.BlogPost.query.order_by(BlogPost.id.desc())
        posts = query.paginate(page, POSTS_PER_PAGE_ADMIN, False)
        return render_template('admin.html', posts=posts)


@app.route('/delete/<int:id>', methods=['POST','GET'])
@login_required
def delete(id):
    post = db.session.query(BlogPost).get(id)
    db.session.delete(post)
    db.session.commit()
    flash('Entry was successfully deleted.')
    return redirect(url_for('admin'))


@app.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit(id):
    post = db.session.query(BlogPost).get(id)
    if request.method=='POST':
        post.title = request.form['title']
        post.pub_date = request.form['pub_date']
        post.content = request.form['content']

        # If choose to upload a new file, then set post.img_url to new file.
        file=request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post.img_url= '/static/img/'+ filename

        # If file format is not allowed, flash a msg and goes back to edit page.
        elif file and not allowed_file(file.filename):
            flash('Only pictures are allowed to be uploaded!')
            return render_template('edit.html', post=post)

        # If no file chosen, post.img_url stays the same as the current one.
        db.session.add(post)
        db.session.commit()

        flash('Your changes have been saved.')
        return redirect(url_for('admin'))

    return render_template('edit.html', post=post)



# open static/img folder
@app.route('/show_imgs',methods=['POST','GET'])
@login_required
def show_imgs():
    imgs = os.listdir(app.config['UPLOAD_FOLDER'])

    return render_template('show_imgs.html',imgs=imgs)


# delete images in static/img folder
@app.route('/remove_img/<img>',methods=['POST','GET'])
@login_required
def remove_img(img):
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img))
    return redirect(url_for('show_imgs'))



#hash username and password during login
@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method=='POST':
    # removed password from main code, only use the hashed encrypted code here.
        pw_hash = 'hashed version of password'

        if request.form['username']!= username:
            error = 'Invalid username. Please try again.'
        elif not bcrypt.check_password_hash(pw_hash, request.form['password']):
            error = 'Invalid password. Please try again.'
        else:
            session['logged_in'] = True
            flash('You are logged in.')
            return redirect(url_for('admin'))

    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You are logged out.')
    return redirect(url_for('login'))


# allowed file upload format
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']







if __name__ == '__main__':
    app.run()
