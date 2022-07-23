from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, Response, abort
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

    results = face_recognition.compare_faces([known_encoding], unknown_encoding,0.4)
    return results[0]

def face_checker(image):
    test_image = face_recognition.load_image_file(image)
    test_encoding = face_recognition.face_encodings(test_image)
    if len(test_encoding) == 0:
        return False
    return True

auth = Blueprint('auth', __name__)


@auth.route('/',methods=['GET','POST'])
@auth.route('/home/')
@login_required
def home():
    flash('You are now logged in', category='success')
    return render_template('index.html')

@auth.route('/login/',methods=['GET','POST'])
def login():
    if(request.method=='POST'):
        uname = request.form.get('uname')
        file = request.files['blob']
        unknwn_read = file.read()
        unknwn = io.BytesIO(unknwn_read)

        if (not face_checker(unknwn)) :
            flash('Face not found', category="error")
            return abort(400)

        user = User.query.filter_by(uname=uname).first()
        if(not user):
            flash('Username not Found', category="error")

        knwn = io.BytesIO(user.image)
        check = recognizer(knwn, unknwn)
        if(not check):
            flash("Faces does not match", category="error")
            return {"code":1}
        login_user(user, remember=True)
        flash('Login Successful', category="success")
        return Response(200)

    return render_template('login.html')

@auth.route('/signup/',methods=['GET','POST'])
def signup():
    if(request.method=='POST'):
        uname = request.form.get('uname')
        email = request.form.get('email')
        file = request.files['blob']
        file_read = file.read()
        knwn = io.BytesIO(file_read)
        
        user = User.query.filter_by(uname=uname).first()
        if(user):
            flash("Username already exists", category="error")
            return {"code":1}

        if (not face_checker(knwn)) :
            flash('Face not found', category="error")
            return {"code":1}

        print("Face detected!")        
        user = User(uname=uname,email=email,image=file_read)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered and can log in',category='success')
        return Response(200)
        
    return render_template('signup.html')

@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))
