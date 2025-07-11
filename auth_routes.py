from flask import Blueprint, request, redirect, render_template, session, url_for
from models import User, SessionLocal
import string
import random
import smtplib
from email.mime.text import MIMEText

auth_bp = Blueprint("auth", __name__)

# ---- LOGIN ----
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        role = request.form.get("role")

        db = SessionLocal()

        if role == "teacher":
            email_or_username = request.form.get("email_or_username")
            password = request.form.get("password")

            user = db.query(User).filter(
                ((User.email == email_or_username) | (User.username == email_or_username)) &
                (User.password == password) &
                (User.role.in_(["teacher", "admin"]))
            ).first()

        elif role == "student":
            student_username = request.form.get("student_username")
            student_password = request.form.get("student_password")
            teacher_username = request.form.get("teacher_username")

            teacher = db.query(User).filter_by(username=teacher_username, role="teacher").first()
            if teacher:
                user = db.query(User).filter_by(
                    username=student_username,
                    password=student_password,
                    role="student",
                    teacher_id=teacher.id
                ).first()
            else:
                user = None

        else:
            user = None

        db.close()

        if user:
            session["user_id"] = user.id
            session["role"] = user.role

            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif user.role == "teacher":
                return redirect(url_for("teacher.dashboard"))
            elif user.role == "student":
                return redirect(url_for("student.dashboard"))
            else:
                error = "Unknown user role."
        else:
            error = "Invalid credentials."

    return render_template("login.html", error=error)


# ---- LOGOUT ----
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# ---- REGISTER TEACHER ----
@auth_bp.route("/register-teacher", methods=["GET", "POST"])
def register_teacher():
    error = None

    if request.method == "POST":
        username=request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        db = SessionLocal()

        existing_mail = db.query(User).filter_by(email=email).first()
        existing_username=db.query(User).filter_by(username=username).first()
        if existing_mail or existing_username:
            error = "Email oder Lehrerkürzel existiert schon."
        else:
            new_teacher = User(email=email, password=password, username=username, role="teacher")
            db.add(new_teacher)
            db.commit()
            db.close()
            return redirect(url_for("auth.login"))

        db.close()

    return render_template("register_teacher.html", error=error)

# Utility: generate random password
def generate_random_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

# Send email using SMTP (for testing with Gmail)
def send_email(to_email, new_password):
    # You can use environment variables later to hide these
    FROM_EMAIL = "youremail@example.com"
    FROM_PASSWORD = "your-email-password"

    subject = "Your New Password"
    body = f"Your new password is: {new_password}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(FROM_EMAIL, FROM_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
            return True
    except Exception as e:
        print("Email error:", e)
        return False
    
    