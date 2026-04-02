# utils/init_superadmin.py
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database.database import engine
from models import database_models
from utils.auth import hash_password

load_dotenv()

def create_superadmin():
    username = os.getenv("SUPERADMIN_USERNAME", "superadmin")
    password = os.getenv("SUPERADMIN_PASSWORD")

    with Session(engine) as db:
        existing = db.query(database_models.User).filter_by(username=username).first()
        if not existing:
            db.add(database_models.User(
                username=username,
                hashed_password=hash_password(password)
            ))
            db.commit()
            print(f"Superadmin '{username}' créé.")
        else:
            print("Superadmin déjà existant.")