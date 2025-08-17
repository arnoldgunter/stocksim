from models import SessionLocal, Stock, StockPriceHistory
from datetime import datetime, timedelta
import random

db = SessionLocal()

# Pick a stock (first one for now)
stock = db.query(Stock).first()

if stock:
    base_price = stock.current_price
    for i in range(48):  # 48 hours of hourly data
        change = random.uniform(-0.02, 0.02) * base_price
        price = round(base_price + change, 2)
        timestamp = datetime.utcnow() - timedelta(hours=(48 - i))
        history = StockPriceHistory(
            stock_id=stock.id,
            price=price,
            timestamp=timestamp
        )
        db.add(history)

    db.commit()
    print(f"Inserted 48 history points for {stock.name}")
else:
    print("No stock found.")

db.close()