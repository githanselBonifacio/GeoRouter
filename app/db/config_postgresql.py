import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/cuida"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()
