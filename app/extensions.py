from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import Config


Base = declarative_base()
engine = create_engine(
	Config.SQLALCHEMY_DATABASE_URI,
	connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)