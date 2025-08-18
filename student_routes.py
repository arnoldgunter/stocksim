from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from models import User, SessionLocal, Stock, StudentStock, StockPriceHistory, Trade
from utils import range_to_start
from datetime import timezone


student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route("/dashboard")
def dashboard():
    if session.get("role") != "student":
        return redirect(url_for("auth.login"))

    db = SessionLocal()
    user = db.query(User).filter_by(id=session["user_id"]).first()

    if not user:
        db.close()
        return redirect(url_for("auth.login"))

    usable_funds = user.funds or 0.0

    # Calculate invested amount
    invested = 0.0
    for holding in user.holdings:
        current_price = holding.stock.current_price
        invested += holding.quantity * current_price

    db.close()

    return render_template("student_dashboard.html",
                           usable_funds=usable_funds,
                           invested_funds=invested)

@student_bp.route("/trade")
def trade():
    db = SessionLocal()
    user_id = session.get("user_id")
    student = db.query(User).filter_by(id=user_id).first()
    stocks = db.query(Stock).order_by(Stock.name).all()
    db.close()
    return render_template("student_trade.html", student=student, stocks=stocks)

@student_bp.route("/change-password", methods=["POST"])
def change_password():
    if session.get("role") != "student":
        return redirect(url_for("auth.login"))

    new_password = request.form.get("new_password")
    db = SessionLocal()
    student = db.query(User).filter_by(id=session["user_id"], role="student").first()

    if not student:
        db.close()
        return redirect(url_for("auth.login"))

    if new_password:
        student.password = new_password
        db.commit()
        db.close()
        flash("✅ Password updated successfully.", "success")
    else:
        db.close()
        flash("❌ Please provide a new password.", "error")

    return redirect(url_for("student.dashboard"))


@student_bp.route("/stock-history/<int:stock_id>")
def student_stock_history(stock_id):
    range_key = request.args.get("range")  # "1d","1w","1m","3m","1y","all"
    start_dt = range_to_start(range_key)

    db = SessionLocal()
    q = db.query(StockPriceHistory).filter_by(stock_id=stock_id)
    if start_dt:
        q = q.filter(StockPriceHistory.timestamp >= start_dt)
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



@student_bp.route("/holdings/<int:stock_id>")
def get_student_holdings(stock_id):
    db = SessionLocal()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    user = db.query(User).get(user_id)
    holding = next((h for h in user.holdings if h.stock_id == stock_id), None)

    quantity = holding.quantity if holding else 0
    stock = db.query(Stock).get(stock_id)
    total_value = quantity * stock.current_price if stock else 0.0

    db.close()
    return jsonify(quantity=quantity, total_value=total_value)

@student_bp.route("/trade-stock", methods=["POST"])
def trade_stock():
    if session.get("role") != "student":
        print("Unauthorized access attempt")
        return {"error": "Unauthorized"}, 403

    data = request.get_json()
    print("Incoming trade request:", data)
    stock_id = int(data.get("stock_id"))
    buy_qty = int(data.get("buy_quantity", 0))
    sell_qty = int(data.get("sell_quantity", 0))

    db = SessionLocal()
    user = db.query(User).get(session["user_id"])
    stock = db.query(Stock).get(stock_id)

    if not stock or not user:
        print("Invalid stock or user")
        db.close()
        return {"error": "Invalid stock or user"}, 400

    total_cost = buy_qty * stock.current_price
    total_earnings = sell_qty * stock.current_price

    print(f"Funds: {user.funds}, Cost: {total_cost}, Earnings: {total_earnings}")

    # Check for sufficient funds
    if total_cost > user.funds:
        print("Not enough funds")
        db.close()
        return {"error": "Not enough funds"}, 400

    # Check if user has stock to sell
    holding = db.query(StudentStock).filter_by(student_id=user.id, stock_id=stock.id).first()
    if sell_qty > 0 and (not holding or holding.quantity < sell_qty):
        print("Not enough shares to sell")
        db.close()
        return {"error": "Not enough shares to sell"}, 400

    # Apply trade
    if total_cost > 0:
        new_trade = Trade(
            student_id=user.id,
            stock_id=stock.id,
            quantity=buy_qty,
            price_at_trade=stock.current_price,
            trade_type="buy"
        )       
        db.add(new_trade)
        user.funds -= total_cost
        if holding:
            holding.quantity += buy_qty
        else:
            holding = StudentStock(student_id=user.id, stock_id=stock.id, quantity=buy_qty)
            db.add(holding)

    if total_earnings > 0:
        holding.quantity -= sell_qty
        user.funds += total_earnings

        if holding.quantity == 0:
            db.delete(holding)

    db.commit()
    db.close()
    print("Trade successful!")

    return {"message": "Trade successful"}

@student_bp.route("/portfolio")
def student_portfolio():
    if session.get("role") != "student":
        return redirect(url_for("auth.login"))

    db = SessionLocal()
    user = db.query(User).get(session["user_id"])
    
    portfolio = []
    for holding in user.holdings:
        stock = holding.stock
        quantity = holding.quantity

        # Get current price
        current_price = stock.current_price
        current_value = round(quantity * current_price, 2)

        # Get total paid using history
        trades = db.query(Trade).filter_by(student_id=user.id, stock_id=stock.id, trade_type="buy").all()
        total_paid = sum(trade.quantity * trade.price_at_trade for trade in trades)

        portfolio.append({
            "stock_id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "quantity": quantity,
            "current_value": current_value,
            "total_paid": round(total_paid, 2),
            "current_price": current_price,
        })

    db.close()

    portfolio = []
    portfolio_names = []
    portfolio_values = []

    for holding in user.holdings:
        stock = holding.stock
        quantity = holding.quantity
        current_price = stock.current_price
        current_value = round(quantity * current_price, 2)

        portfolio_names.append(stock.name)
        portfolio_values.append(current_value)

        trades = db.query(Trade).filter_by(student_id=user.id, stock_id=stock.id, trade_type="buy").all()
        total_paid = sum(trade.quantity * trade.price_at_trade for trade in trades)

        portfolio.append({
            "stock_id": stock.id,
            "symbol": stock.symbol,
            "name": stock.name,
            "quantity": quantity,
            "current_price": current_price,
            "total_value": round(quantity * stock.current_price, 2),
            "total_paid": round(total_paid, 2),
            "current_price": current_price,
        })

    return render_template(
        "student_portfolio.html",
        portfolio=portfolio,
        portfolio_names=portfolio_names,
        portfolio_values=portfolio_values,
    )

from collections import defaultdict
from datetime import datetime
from flask import jsonify, session
from sqlalchemy.orm import joinedload

@student_bp.route("/portfolio-history")
def get_portfolio_history():
    if session.get("role") != "student":
        return jsonify({"error": "Unauthorized"}), 403

    db = SessionLocal()
    student_id = session["user_id"]

    # Get student's trades in time order
    trades = (
        db.query(Trade)
        .filter_by(student_id=student_id)
        .order_by(Trade.timestamp.asc())
        .all()
    )

    # If no trades, just return empty
    if not trades:
        db.close()
        return jsonify([])

    # Collect stock_ids involved (only those the student traded)
    stock_ids = sorted({t.stock_id for t in trades})

    # Load price histories for these stocks
    histories = {}
    all_timestamps = set()
    for sid in stock_ids:
        hist = (
            db.query(StockPriceHistory)
            .filter_by(stock_id=sid)
            .order_by(StockPriceHistory.timestamp.asc())
            .all()
        )
        if not hist:
            # if a stock lacks history, skip (or use trade prices only)
            histories[sid] = []
            continue
        histories[sid] = hist
        for h in hist:
            all_timestamps.add(h.timestamp)

    # Also include trade timestamps (so we value right after trades happen)
    for t in trades:
        all_timestamps.add(t.timestamp)

    sorted_ts = sorted(all_timestamps)

    # Pointers / state for single-pass evaluation
    trade_idx = 0
    holdings = defaultdict(int)  # stock_id -> quantity
    price_ptr = {sid: 0 for sid in stock_ids}  # pointer into each stock's history
    current_price = {sid: None for sid in stock_ids}

    # Initialize current_price to first known price (if any)
    for sid in stock_ids:
        if histories[sid]:
            current_price[sid] = histories[sid][0].price

    results = []

    # Walk forward in time
    for ts in sorted_ts:
        # 1) Advance price pointers up to current timestamp
        for sid in stock_ids:
            hist = histories[sid]
            ptr = price_ptr[sid]
            while ptr < len(hist) and hist[ptr].timestamp <= ts:
                current_price[sid] = hist[ptr].price
                ptr += 1
            price_ptr[sid] = ptr

        # 2) Apply trades that occur at/before current timestamp (each trade exactly once)
        while trade_idx < len(trades) and trades[trade_idx].timestamp <= ts:
            tr = trades[trade_idx]
            if tr.trade_type == "buy":
                holdings[tr.stock_id] += tr.quantity
            elif tr.trade_type == "sell":
                holdings[tr.stock_id] -= tr.quantity
            trade_idx += 1

        # 3) Compute total value at this timestamp (ONLY stocks with qty > 0)
        total_value = 0.0
        for sid, qty in holdings.items():
            if qty <= 0:
                continue
            price = current_price.get(sid)
            if price is not None:
                total_value += qty * price

        results.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
            "value": round(total_value, 2)
        })

    db.close()
    return jsonify(results)