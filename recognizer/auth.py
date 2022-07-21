from flask import Blueprint, render_template, request, redirect, url_for, flash
from .modals import User
from . import db
import face_recognition
from flask_login import login_required, login_user, current_user, logout_user
import io

def recognizer(known, unknown):
    known_image = face_recognition.load_image_file(known)
    unknown_image = face_recognition.load_image_file(unknown)

    known_encoding = face_recognition.face_encodings(known_image)[0]
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    results = face_recognition.compare_faces([known_encoding], unknown_encoding)
    return results[0]


auth = Blueprint('auth', __name__)


@auth.route('/login/',methods=['GET','POST'])
@auth.route('/',methods=['GET','POST'])
def login():
    if(request.method=='POST'):
        uname = request.form.get('uname')
        file = request.files['blob']
        user = User.query.filter_by(uname=uname).first()
        unknwn = io.BytesIO(file.read())
        knwn = io.BytesIO(user.image)
        check = recognizer(knwn, unknwn)
        print(check)
        if(check):
            login_user(user)
            flash('Login Successful')
            return redirect(url_for('auth.home'))
        else:
            flash("Try Again")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/signup/',methods=['GET','POST'])
def signup():
    if(request.method=='POST'):
        uname = request.form.get('uname')
        email = request.form.get('email')

        file = request.files['blob']

        user = User(uname=uname,email=email,image=file.read())
        db.session.add(user)
        db.session.commit()
        flash('You are now registered and can log in')
        return redirect(url_for('auth.login'))
        
    return render_template('signup.html')

@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))

@auth.route('/home/')
@login_required
def home():
    flash('You are now logged in')
    return render_template('index.html')