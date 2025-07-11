from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify, flash
from models import User, SessionLocal, Stock, StockPriceHistory
from sqlalchemy.orm import joinedload

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    db = SessionLocal()
    error = None
    success = None

    if request.method == "POST":
        action = request.form.get("action")
        user_id = request.form.get("user_id")

        user = db.query(User).filter_by(id=user_id).first()

        if user:
            if action == "delete":
                # Delete a teacher and their students, or a single student
                if user.role == "teacher":
                    # Delete associated students first
                    for student in user.students:
                        db.delete(student)
                    db.delete(user)
                    db.commit()
                    success = f"Deleted teacher {user.email} and their students."
                elif user.role == "student":
                    db.delete(user)
                    db.commit()
                    success = f"Deleted student {user.username}."
            elif action == "change_password":
                new_password = request.form.get("new_password")
                if new_password:
                    user.password = new_password
                    db.commit()
                    success = f"Password updated for {user.email or user.username}."
                else:
                    error = "New password not provided."
        else:
            error = "User not found."

    # Get teachers sorted alphabetically
    teachers = db.query(User)\
    .options(joinedload(User.students))\
    .filter_by(role="teacher")\
    .order_by(User.email.asc())\
    .all()

    for t in teachers:
        print(f"Teacher: {t.email}")
        if t.students:
            print("  Students:", [s.username for s in t.students])
        else:
            print("  No students.")

    return render_template("admin_dashboard.html", teachers=teachers, error=error, success=success)

@admin_bp.route("/admin/stocks", methods=["GET", "POST"])
def manage_stocks():
    db = SessionLocal()

    if request.method == "POST":
        stock_id = request.form.get("stock_id")
        new_price = request.form.get("new_price")
        new_volatility = request.form.get("new_volatility")
        new_trend = request.form.get("new_trend")

        try:
            stock = db.query(Stock).filter_by(id=stock_id).first()
            if stock:
                if new_price:
                    stock.current_price = round(float(new_price), 2)
                if new_volatility:
                    stock.volatility = round(float(new_volatility), 3)
                if new_trend:
                    stock.monthly_target_change = round(float(new_trend), 3)
                db.commit()
        except Exception as e:
            print("Update error:", e)

        return redirect(url_for("admin.manage_stocks"))

    stocks = db.query(Stock).order_by(Stock.name).all()
    db.close()
    return render_template("manage_stocks.html", stocks=stocks)

@admin_bp.route("/stock-history/<int:stock_id>")
def stock_history(stock_id):
    db = SessionLocal()
    history = (
        db.query(StockPriceHistory)
        .filter_by(stock_id=stock_id)
        .order_by(StockPriceHistory.timestamp)
        .limit(100)  # last 100 points
        .all()
    )
    db.close()

    data = [
        {"timestamp": h.timestamp.strftime("%Y-%m-%d %H:%M"), "price": h.price}
        for h in history
    ]
    return jsonify(data)

@admin_bp.route("/clear-stock-history", methods=["POST"])
def clear_stock_history():
    db = SessionLocal()
    try:
        deleted = db.query(StockPriceHistory).delete()
        db.commit()
        print(f"Deleted {deleted} stock history entries.")
        flash("All stock history has been cleared.", "success")
    except Exception as e:
        print("Error clearing stock history:", e)
        flash("Failed to clear stock history.", "error")
    finally:
        db.close()

    return redirect(url_for("admin.manage_stocks"))