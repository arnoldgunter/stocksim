from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

# Base class for all models
Base = declarative_base()

# User table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)  # optional for students
    username = Column(String)  # required for students
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "admin", "teacher", "student"
    funds = Column(Float, default=0.0)

    # Student-to-teacher association
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    teacher = relationship("User", remote_side=[id], back_populates="students")
    students = relationship("User", back_populates="teacher")

    # Stock holdings
    holdings = relationship("StudentStock", back_populates="student", cascade="all, delete-orphan")

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    volatility=Column(Float)
    category=Column(String)
    monthly_target_change = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow())

class StockPriceHistory(Base):
    __tablename__ = "stock_price_history"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    stock = relationship("Stock")

class StudentStock(Base):
    __tablename__ = "student_stocks"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

    student = relationship("User", back_populates="holdings")
    stock = relationship("Stock")

    from datetime import datetime

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    quantity = Column(Integer, nullable=False)
    price_at_trade = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    trade_type = Column(String, nullable=False)  # 'buy' or 'sell'

    student = relationship("User")
    stock = relationship("Stock")



# Connect to the database
engine = create_engine("sqlite:///stock_sim.db")
Base.metadata.create_all(engine)

# Create session factory
SessionLocal = sessionmaker(bind=engine)