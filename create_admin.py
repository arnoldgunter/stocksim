from models import User, SessionLocal

# Create a database session
db = SessionLocal()

# Check if an admin already exists
existing = db.query(User).filter_by(role="admin").first()

if existing:
    print("Admin already exists:", existing.email)
else:
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    admin = User(email=email, password=password, role="admin")
    db.add(admin)
    db.commit()
    print("Admin created successfully.")

db.close()