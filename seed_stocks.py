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
        ("OLSM", "Olkasor Silvermines", 22.34, 0.002, "Certificate", 0.03),
        ("GREC", "Gulriath Empire ETF", 32.00, 0.005, "ETF", 0.06),
        ("GUVR", "Haven Union of Guvan", 34.20, 0.25, "ETF", -0.02),
        ("ISLC", "Confederation of Isles Port Bond", 67.80, 0.07, "ETF", 0.02),
        ("ELSW", "Elswary Love Bond", 34.90, 0.03, "Fund", 0.01),
        ("PIRE", "Elsmaril Pirate Dubloons", 105.50, 0.2, "Crypto", -0.10),
        ("XTRX", "Kvexhall Fir Plantery", 18.75, 0.005, "Fund", 0.01),
        ("QUAD", "Quadratische Funktionen ETF", 3.20, 0.25, "ETF", 0.50),
        ("SEND", "Sender's Super Coin", 67.80, 0.4, "ETF", 0.02),
        ("DRGNX", "Dragonfire Holdings", 120.50, 0.08, "Stock", 0.03),
        ("MANA", "ManaCoin", 1.23, 0.25, "Crypto", 0.12),
        ("ELVEN", "Elven Forestry Fund", 87.40, 0.015, "Fund", 0.01),
        ("DWARF", "Dwarven Forge Ltd.", 45.30, 0.04, "Stock", 0.02),
        ("SHDW", "Shadow Guild ETF", 66.00, 0.07, "ETF", -0.01),
        ("WZRD", "Wizard Tower Investments", 99.99, 0.03, "Stock", 0.015),
        ("NEXUS", "Planar Nexus Portals Inc.", 210.25, 0.06, "Stock", 0.08),
        ("LICH", "LichCoin", 0.78, 0.35, "Crypto", -0.05),
        ("FAIRY", "Fairy Dust Ventures", 52.70, 0.09, "Stock", 0.07),
        ("MORDR", "Mordrath Armaments", 134.10, 0.12, "Stock", -0.02),
        ("PHNX", "Phoenix Rebirth Fund", 88.88, 0.02, "Fund", 0.025),
        ("GRIMG", "Grim Grimoire Ltd.", 32.60, 0.10, "Stock", 0.03),
        ("CRYST", "Crystal Shard Mining Co.", 18.20, 0.05, "Stock", 0.01),
        ("GLMR", "GlamourCoin", 3.50, 0.30, "Crypto", 0.20),
        ("OGREX", "Ogre Express Logistics", 55.00, 0.06, "Stock", 0.005),
        ("QZDZR", "Basilisk Collective", 200.65, 0.020, "ETF", 0.014),
        ("WZFQJ", "Twilight Coin", 234.53, 0.146, "Stock", -0.043),
        ("GYNSK", "Goblin Logistics", 38.93, 0.174, "ETF", 0.142),
        ("GRPNM", "Wyrm Capital", 214.66, 0.044, "ETF", 0.122),
        ("VACJM", "Elder Consortium", 5.63, 0.168, "ETF", 0.056),
        ("QEXDN", "Blood Ministries", 180.33, 0.202, "Crypto", 0.074),
        ("BZCQL", "Obsidian Coin", 72.18, 0.049, "Fund", -0.049),
        ("NVCFA", "Twilight Guild", 53.29, 0.204, "Crypto", 0.044),
        ("THGMX", "Crystal Logistics", 205.39, 0.021, "Crypto", -0.009),
        ("FSWBI", "Sapphire Coin", 39.88, 0.112, "Fund", 0.047),
        ("SYNXZ", "Griffin Matrix", 68.86, 0.295, "Stock", -0.015),
        ("IVWBN", "Fae Fund", 236.95, 0.027, "ETF", 0.077),
        ("UYVGI", "Thorn Logistics", 143.86, 0.277, "Fund", 0.124),
        ("RMFVE", "Rune Bank", 44.16, 0.274, "Stock", 0.090),
        ("AVVJU", "Fae Coin", 96.61, 0.298, "ETF", -0.011),
        ("GXWZV", "Void Logistics", 17.24, 0.293, "Stock", 0.055),
        ("JAVYM", "Nether Logistics", 120.16, 0.042, "Stock", -0.002),
        ("VDXQL", "Moonshade Holdings", 49.27, 0.027, "Stock", 0.130),
        ("IYJXN", "Griffin Bank", 88.08, 0.009, "Crypto", 0.114),
        ("SHBYP", "Basilisk Guild", 55.55, 0.146, "ETF", -0.049),
        ("OUKPA", "Blood Coin", 182.39, 0.126, "Stock", 0.172),
        ("RHCSW", "Storm Coin", 236.84, 0.059, "Fund", 0.122),
        ("YXKNR", "Oak Union", 131.16, 0.025, "Stock", 0.081),
        ("DYULI", "Blood Initiative", 94.55, 0.145, "ETF", 0.158),
        ("BCELK", "Twilight Union", 246.85, 0.296, "Stock", 0.119),
        ("CMEUQ", "Crystal Coin", 28.45, 0.291, "Stock", -0.019),
        ("ZXKDE", "Witch Enterprises", 169.81, 0.288, "Stock", 0.063),
        ("LMSWZ", "Goblin Coin", 147.42, 0.027, "Stock", 0.176),
        ("WYZPR", "Oak Limited", 29.74, 0.200, "Crypto", 0.018),
        ("NXCKM", "Mythril Ministries", 15.89, 0.292, "Fund", 0.035),
        ("AYWEG", "Void Bank", 33.02, 0.017, "Fund", 0.034),
        ("NHAVF", "Celestial Ministries", 81.35, 0.096, "ETF", -0.024),
        ("FNSZP", "Basilisk Capital", 42.07, 0.277, "ETF", 0.018),
        ("QEDWA", "Obsidian Ventures", 60.08, 0.120, "Stock", 0.133),
        ("OTUZA", "Ashen Fund", 8.17, 0.129, "ETF", 0.027),
        ("ATBKH", "Void Coin", 114.61, 0.290, "Crypto", 0.067),
        ("ZUCJT", "Wyrm Coin", 156.30, 0.250, "Stock", -0.004),
        ("ABWQU", "Twilight Ministries", 71.24, 0.194, "Stock", 0.015),
        ("YTIRH", "Griffin Coin", 4.93, 0.008, "Crypto", -0.007),
        ("UADTO", "Obsidian Matrix", 18.65, 0.030, "ETF", 0.036),
        ("YHGLD", "Flame Bank", 62.42, 0.022, "Fund", -0.043),
        ("UNFEM", "Twilight Fund", 60.93, 0.156, "Stock", -0.048),
        ("UOXDY", "Fae Logistics", 189.87, 0.163, "ETF", 0.149),
        ("UNIXD", "Basilisk Bank", 140.92, 0.243, "ETF", 0.084),
        ("IGWPL", "Goblin Holdings", 116.46, 0.144, "Crypto", -0.018),
        ("SEHXO", "Wyrm Matrix", 66.06, 0.248, "Stock", 0.050),
        ("TOJDK", "Witch Union", 126.18, 0.141, "ETF", -0.018),
        ("OPXYG", "Moonshade Matrix", 248.12, 0.035, "ETF", -0.021),
        ("BAKQI", "Nether Union", 170.88, 0.079, "Crypto", 0.037),
        ("GJSTC", "Storm Ministries", 222.51, 0.153, "Fund", 0.106),
        ("GOUXB", "Witch Capital", 12.61, 0.295, "Stock", 0.084),
        ("EXSPY", "Witch Logistics", 42.94, 0.242, "ETF", -0.031),
        ("QNMCP", "Void Holdings", 234.00, 0.184, "Crypto", -0.043),
        ("MPRJU", "Celestial Bank", 92.61, 0.139, "Stock", 0.026),
        ("CNSRJ", "Obsidian Guild", 229.87, 0.118, "Crypto", 0.121),
        ("HXMFA", "Moonshade Ventures", 176.45, 0.260, "Stock", 0.051),
        ("VYMEI", "Spell Union", 13.83, 0.118, "ETF", 0.161),
        ("IICQZ", "Ashen Bank", 62.89, 0.021, "Fund", 0.011),
        ("XLNWH", "Obsidian Union", 104.58, 0.182, "Crypto", 0.090),
        ("MWBDP", "Griffin Union", 202.00, 0.254, "ETF", -0.029),
        ("KJXDF", "Flame Ministries", 83.93, 0.017, "Crypto", 0.038),
        ("TPWSI", "Storm Guild", 99.55, 0.205, "ETF", 0.125),
        ("UAVRN", "Oak Enterprises", 38.12, 0.222, "ETF", -0.028),
        ("YNDCK", "Goblin Ventures", 153.79, 0.088, "Crypto", -0.037),
        ("CVYGT", "Void Union", 178.27, 0.035, "Stock", 0.011),
        ("LEZCT", "Void Matrix", 14.27, 0.102, "ETF", -0.050),
        ("MYBCU", "Fae Bank", 200.70, 0.233, "ETF", 0.052),
        ("MNIDK", "Crystal Ventures", 85.40, 0.224, "ETF", 0.062),
        ("MIFVU", "Celestial Ventures", 153.70, 0.107, "Crypto", -0.005),
        ("XOVHK", "Void Syndicate", 215.95, 0.123, "ETF", -0.014),
        ("SVOWC", "Crystal Holdings", 145.21, 0.126, "Stock", 0.019),
        ("WWCSF", "Oak Capital", 129.52, 0.056, "Crypto", 0.032),
        ("BWMSU", "Rune Union", 168.74, 0.017, "Crypto", 0.139),
        ("YWKNH", "Moonshade Guild", 227.94, 0.238, "ETF", -0.012),
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