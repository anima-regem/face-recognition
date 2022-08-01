from crypt import methods
from ctypes import sizeof
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Response,
    abort,
)
from .modals import User
from . import db, client
import face_recognition
from flask_login import login_required, login_user, current_user, logout_user
import io
from .blink_detection import blink_detector
from random import randint


global user
user = User()
auth = Blueprint("auth", __name__)


def recognizer(known, unknown):
    known_image = face_recognition.load_image_file(known)
    unknown_image = face_recognition.load_image_file(unknown)
    known_encoding = face_recognition.face_encodings(known_image)[0]
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
    results = face_recognition.compare_faces([known_encoding], unknown_encoding, 0.4)
    return results[0]


def face_checker(image):
    test_image = face_recognition.load_image_file(image)
    test_encoding = face_recognition.face_encodings(test_image)
    if len(test_encoding) == 0:
        return False
    return True


@auth.route("/", methods=["GET", "POST"])
@auth.route("/home/")
@login_required
def home():
    flash("You are now logged in", category="success")
    return render_template("index.html")


@auth.route("/validate/", methods=["POST"])
def validate():
    knwn_otp = user.otp
    otp = request.form.get("otp")
    if str(knwn_otp) == str(otp):
        user.logged = True
        login_user(user)
        return redirect(url_for("auth.home"))
    return redirect(url_for("auth.login"))


@auth.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        global user
        uname = request.form.get("uname")
        file = request.files["blob"]
        video = request.files["video"]
        videoData = video.read()
        videoFile = io.BytesIO(videoData)
        videoFile.seek(0)
        with open("my_file.webm", "wb") as binary_file:
            binary_file.write(videoData)
        blinking = blink_detector()
        if not blinking:
            flash("Blink Not detected", category="danger")
            return abort(400)
        unknwn_read = file.read()
        unknwn = io.BytesIO(unknwn_read)
        if not face_checker(unknwn):
            flash("Face not found", category="error")
            return abort(400)
        user = User.query.filter_by(uname=uname).first()
        if not user:
            flash("Username not Found", category="error")
        knwn = io.BytesIO(user.image)
        check = recognizer(knwn, unknwn)
        if not check:
            flash("Faces does not match", category="error")
            return abort(400)
        user.logged = False
        flash("Login Successful", category="success")
        knwn_otp = randint(0000, 9999)
        user.otp = knwn_otp
        phone = user.phone
        body = "Your OTP is " + str(knwn_otp)
        message = client.messages.create(from_="+13186677783", body=body, to=phone)
        return render_template("verify.html")
    if current_user.is_authenticated:
        return redirect(url_for("auth.home"))
    return render_template("login.html")


@auth.route("/signup/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        uname = request.form.get("uname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        file = request.files["blob"]
        file_read = file.read()
        knwn = io.BytesIO(file_read)
        user = User.query.filter_by(uname=uname).first()
        if user:
            flash("Username already exists", category="error")
            return abort(400)
        if not face_checker(knwn):
            flash("Face not found", category="error")
            return abort(400)
        user = User(uname=uname, email=email, phone=phone, image=file_read)
        db.session.add(user)
        db.session.commit()
        flash("You are now registered and can log in", category="success")
        return redirect(url_for("auth.login"))
    if current_user.is_authenticated:
        return redirect(url_for("auth.home"))
    return render_template("signup.html")


@auth.route("/logout/")
@login_required
def logout():
    user.logged = False
    logout_user()
    flash("You have been logged out.", category="success")
    return redirect(url_for("auth.login"))
