from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models import SessionLocal, User, Trade, StockPriceHistory, Stock
from sqlalchemy.orm import joinedload

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@teacher_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # Redirect if not logged in as teacher
    if session.get("role") != "teacher":
        return redirect(url_for("auth.login"))

    db = SessionLocal()
    teacher = db.query(User).filter_by(id=session["user_id"]).first()

    error = None
    success = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_student":
            username = request.form.get("username")
            password = request.form.get("password")
            funds = float(request.form.get("funds") or 0)

            if not username or not password:
                error = "Username and password are required."
            elif db.query(User).filter_by(username=username, teacher_id=teacher.id).first():
                error = "You already have a student with that username."
            else:
                new_student = User(
                    username=username,
                    password=password,
                    role="student",
                    funds=funds,
                    teacher_id=teacher.id
                )
                db.add(new_student)
                db.commit()
                success = f"Student {username} added."

        elif action == "add_funds":
            student_id = request.form.get("student_id")
            amount = float(request.form.get("amount") or 0)
            student = db.query(User).filter_by(id=student_id, role="student", teacher_id=teacher.id).first()
            if student:
                student.funds += amount
                db.commit()
                success = f"Added ${amount:.2f} to {student.username}."
            else:
                error = "Student not found."

        elif action == "change_password":
            student_id = request.form.get("student_id")
            new_password = request.form.get("new_password")
            student = db.query(User).filter_by(id=student_id, role="student", teacher_id=teacher.id).first()
            if student:
                student.password = new_password
                db.commit()
                success = f"Password updated for {student.username}."
            else:
                error = "Student not found."

        elif action == "delete_student":
            student_id = request.form.get("student_id")
            student = db.query(User).filter_by(id=student_id, role="student", teacher_id=teacher.id).first()
            if student:
                db.delete(student)
                db.commit()
                success = f"Deleted student {student.username}."
            else:
                error = "Student not found or doesn't belong to you."

    db.refresh(teacher)
    students = sorted(teacher.students, key=lambda s: s.username.lower())  # This is populated via the relationship
    db.close()

    return render_template(
        "teacher_dashboard.html",
        teacher=teacher,
        students=students,
        error=error,
        success=success
    )

@teacher_bp.route("/view-portfolio/<int:student_id>")
def view_student_portfolio(student_id):
    if session.get("role") != "teacher":
        return redirect(url_for("auth.login"))

    db = SessionLocal()
    teacher_id = session.get("user_id")
    student = db.query(User).filter_by(id=student_id, role="student", teacher_id=teacher_id).first()

    if not student:
        db.close()
        return "Student not found or not assigned to this teacher.", 403

    portfolio = []
    portfolio_names = []
    portfolio_values = []

    for holding in student.holdings:
        stock = holding.stock
        quantity = holding.quantity
        current_price = stock.current_price
        current_value = round(quantity * current_price, 2)

        trades = db.query(Trade).filter_by(student_id=student.id, stock_id=stock.id, trade_type="buy").all()
        total_paid = sum(trade.quantity * trade.price_at_trade for trade in trades)

        portfolio.append({
            "stock_id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "quantity": quantity,
            "current_price": current_price,
            "current_value": current_value,
            "total_paid": round(total_paid, 2)
        })

        if quantity > 0:
            portfolio_names.append(stock.name)
            portfolio_values.append(current_value)

    db.close()
    return render_template("view_student_portfolio.html",
                           portfolio=portfolio,
                           student=student,
                           portfolio_names=portfolio_names,
                           portfolio_values=portfolio_values)

@teacher_bp.route("/stock-history/<int:stock_id>")
def teacher_stock_history(stock_id):
    db = SessionLocal()
    history = (
        db.query(StockPriceHistory)
        .filter_by(stock_id=stock_id)
        .order_by(StockPriceHistory.timestamp.asc())
        .all()
    )
    db.close()

    return jsonify([
        {"timestamp": h.timestamp.strftime("%Y-%m-%d %H:%M"), "price": h.price}
        for h in history
    ])

@teacher_bp.route("/student/<int:student_id>/portfolio-history")
def student_portfolio_history(student_id):
    if session.get("role") != "teacher":
        return {"error": "Unauthorized"}, 403

    db = SessionLocal()
    student = db.query(User).filter_by(id=student_id, role="student").first()
    if not student:
        db.close()
        return {"error": "Invalid student"}, 404

    # Get all price timestamps for all stocks the student owns
    all_timestamps = set()
    stock_price_map = {}

    for holding in student.holdings:
        stock_id = holding.stock_id
        history = (
            db.query(StockPriceHistory)
            .filter_by(stock_id=stock_id)
            .order_by(StockPriceHistory.timestamp.asc())
            .all()
        )
        stock_price_map[stock_id] = history
        for record in history:
            all_timestamps.add(record.timestamp)

    # Sort timestamps
    sorted_timestamps = sorted(all_timestamps)

    # Get student trades for computing share ownership over time
    trades = (
        db.query(Trade)
        .filter_by(student_id=student.id)
        .order_by(Trade.timestamp.asc())
        .all()
    )

    # Build portfolio value timeline
    portfolio_history = []
    holdings_tracker = {}  # stock_id -> quantity

    for timestamp in sorted_timestamps:
        # Update holdings as of this timestamp
        for trade in trades:
            if trade.timestamp <= timestamp:
                holdings_tracker.setdefault(trade.stock_id, 0)
                if trade.trade_type == "buy":
                    holdings_tracker[trade.stock_id] += trade.quantity
                elif trade.trade_type == "sell":
                    holdings_tracker[trade.stock_id] -= trade.quantity
            else:
                break  # future trades don't apply yet

        # Calculate value at this timestamp
        total_value = 0.0
        for stock_id, quantity in holdings_tracker.items():
            if quantity <= 0:
                continue
            history = stock_price_map.get(stock_id, [])
            price_at_time = next((h.price for h in reversed(history) if h.timestamp <= timestamp), None)
            if price_at_time is not None:
                total_value += quantity * price_at_time

        portfolio_history.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M"),
            "value": round(total_value, 2)
        })

    db.close()
    return jsonify(portfolio_history)