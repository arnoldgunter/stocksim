from models import SessionLocal, Stock

def seed_stocks():
    db = SessionLocal()

    # Safety check: skip if stocks already exist
    if db.query(Stock).count() > 0:
        print("Stocks already seeded.")
        db.close()
        return

    stocks_to_add = [
        # (symbol, name, price, volatility, category, monthly_change)
        ("OLSM", "Olkasor Silberminen", 22.34, 0.002, "Certificate", 0.03),
        ("GREC", "Kaiserreich Gulriath ETF", 32.00, 0.05, "ETF", 0.06),
        ("GUVR", "Hafenförderation in Guvan ETF", 34.20, 0.25, "ETF", -0.01),
        ("ISLC", "Inselbund Bond", 67.80, 0.07, "ETF", 0.02),
        ("ELSW", "Elswary - Stadt der Liebe - Fonds", 34.90, 0.03, "Fund", 0.01),
        ("PIRE", "Elsmaril Priaten Dublonen (Crypto)", 105.50, 0.2, "Crypto", -0.10),
        ("XTRX", "Kvexhall Fichtenplantagen", 18.75, 0.005, "Fund", 0.01),
        ("QUAD", "Quadratische Funktionen ETF", 3.20, 0.25, "ETF", 0.05),
        ("SEND", "Sender's Super Coin", 67.80, 0.4, "ETF", 0.0),
        ("DRGNX", "Drachenfeuer Schmiedeerzeugnisse", 120.50, 0.08, "Stock", -0.03),
        ("MANA", "ManaCoin", 1.23, 0.8, "Crypto", 0.1),
        ("ELVEN", "Boendil Silbererzeugnisse", 87.40, 0.015, "Fund", 0.01),
        ("ZWRG", "Zwergenstahl", 45.30, 0.04, "Stock", 0.02),
        ("ELSC", "Olkasor Möbelexporte", 12.1, 0.07, "Stock", 0.01),
        ("BUTR", "Schmetterlings COIN", 7.72, 0.24, "Stock", -0.02),
        ("WEBR", "Qoth Textilindustrien", 32.64, 0.04, "Stock", 0.03),
        ("LUND", "Lundenhafen Pökelsalz", 107.22, 0.01, "Stock", 0.01),
        ("FEEN", "Feenstaubverbund Crypto", 0.23, 0.69, "Crypto", 0.12),
        ("A10B", "Aktie für die Klasse 10B", 1.00, 0.04, "Stock", 0.0),
        ("GUVD", "Guvdraijinice Schiffeversicherungen", 23.56, 0.01, "Stock", -0.01),
    ]

    for symbol, name, price, vol, category, monthly_change in stocks_to_add:
        stock = Stock(
            symbol=symbol,
            name=name,
            current_price=price,
            volatility=vol,
            category=category,
            monthly_target_change=monthly_change
        )
        db.add(stock)

    db.commit()
    db.close()
    print(f"Seeded {len(stocks_to_add)} stocks.")

if __name__ == "__main__":
    seed_stocks()
