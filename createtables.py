from models import UserDB, Base
from connect import engine

print("[SQLAlchemy] Creating tables...")
Base.metadata.create_all(bind=engine)
