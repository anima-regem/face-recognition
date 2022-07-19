from flask import Blueprint, render_template, request
from .modals import User
from . import db
import face_recognition

def recognizer(known, unknown):
    known_image = face_recognition.load_image_file(known)
    unknown_image = face_recognition.load_image_file(unknown)

    known_encoding = face_recognition.face_encodings(known_image)[0]
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

    results = face_recognition.compare_faces([known_encoding], unknown_encoding)
    print((results))


auth = Blueprint('auth', __name__)


@auth.route('/login/',methods=['GET','POST'])
def login():
    if(request.method=='POST'):
        uname = request.form.get('uname')
        dataurl = request.form.get('dataurl')
        file = request.files['blob']
        

    return render_template('login.html')

@auth.route('/signup/',methods=['GET','POST'])
def signup():
    if(request.method=='POST'):
        uname = request.form.get('uname')
        email = request.form.get('email')
        password = request.form.get('password')
        dataurl = request.form.get('dataurl')
        file = request.files['blob']

        user = User(uname=uname,email=email,password=password,image=file.read())
        db.session.add(user)
        db.session.commit()

        

        
    return render_template('signup.html')

