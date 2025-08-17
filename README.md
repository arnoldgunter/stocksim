# StockSim

StockSim is a web-based stock market simulator designed for school students to learn about the economy and stock trading. The platform provides a safe and interactive environment for students and teachers to explore financial concepts and practice trading with virtual money.

## Features
- Registration and login for different roles (Admin, Teacher, Student)
- Management of students and teachers
- Simulated stock trading with virtual funds
- Portfolio and trade management
- Stock price history and analytics
- Admin and teacher dashboards

## Installation
1. **Clone the repository**
   ```bash
   git clone <REPO-URL>
   cd stocksim
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize the database**
   The database will be created automatically on first start. Optionally, you can use `seed_stocks.py` to populate it with sample data.
   ```bash
   python seed_stocks.py
   ```
4. **Start the server**
   ```bash
   python app.py
   ```

## Usage
- Open the web application in your browser at `http://localhost:5000`
- Register as a teacher or admin to invite students
- Students can buy/sell stocks and manage their portfolios

## Project Structure
- `app.py` – Main application (Flask)
- `models.py` – Database models (SQLAlchemy)
- `*_routes.py` – Routes for different roles and features
- `templates/` – HTML templates for the web interface
- `static/` – Static files (e.g. CSS)
- `requirements.txt` – Python dependencies
- `stock_sim.db` – SQLite database
