from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

engine = create_engine(os.environ['MYSQL_CONNECTION'], echo=True)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
session = Session()

def init_db():
    import models
    Base.metadata.create_all(engine)

init_db()