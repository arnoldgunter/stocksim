import random
from math import pow
from datetime import datetime
from models import SessionLocal, Stock, StockPriceHistory

def update_stock_prices():
    db = SessionLocal()
    stocks = db.query(Stock).all()

    for stock in stocks:
        # Random component (volatility)
        random_component = random.uniform(-1, 1) * stock.volatility

        # Long-term trend component (based on monthly_target_change)
        hourly_target = pow(1 + stock.monthly_target_change, 1/720) - 1

        # Total change
        change_factor = random_component + hourly_target

        # Apply update
        new_price = max(0.01, stock.current_price * (1 + change_factor))
        stock.current_price = round(new_price, 2)

        # Log price history
        db.add(StockPriceHistory(
            stock_id=stock.id,
            price=stock.current_price,
            timestamp=datetime.utcnow()
        ))

    db.commit()
    db.close()
    print("Prices updated.")