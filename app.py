from flask import Flask, redirect, url_for
from auth_routes import auth_bp
from teacher_routes import teacher_bp
from admin_routes import admin_bp
from student_routes import student_bp
from models import User, SessionLocal #DELETE ONCE SHIPPING
from apscheduler.schedulers.background import BackgroundScheduler
from update_prices import update_stock_prices  # adjust to match your actual method


app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Required for sessions

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)

@app.route("/")
def index():
    return redirect(url_for("auth.login"))  # Or whichever route you want as your landing page

#DELETE WHEN SHIPPING!!!
@app.route("/debug-users")
def debug_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return "<br>".join([f"{u.id}: {u.username or u.email} ({u.role})" for u in users])
#DELETE WHEN SHIPPING END!!!

for i in range(1, 6):
    update_stock_prices()
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_stock_prices, trigger="interval", hours=1)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
