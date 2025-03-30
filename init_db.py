from app import app, db  # Import your Flask app and db from app.py

with app.app_context():
    db.create_all()
    print("Database tables created.")
