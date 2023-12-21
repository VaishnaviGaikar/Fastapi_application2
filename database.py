from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional
from sqlalchemy.orm import sessionmaker

dbcon = "mysql+pymysql://root:123@localhost/vaishnavi"

engine = create_engine(dbcon)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
db = Session()


DATABASE_URL: Optional[str] = None
SECRET_KEY: Optional[str] = "cairocoders"

def get_db():
    new_db = db
    try:
        yield new_db
    finally:
        new_db.close()

