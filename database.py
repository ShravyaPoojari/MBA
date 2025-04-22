from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

# Properly escape special characters in the password
password = quote_plus("Sony@123")  # URL encode the password to handle special characters
DATABASE_URL = f"postgresql://postgres:{password}@localhost:5432/market_basket_analysis"

# Create the database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=3600    # Recycle connections after 1 hour
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
