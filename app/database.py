from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker


# Setting up database hre
DATABASE_URL = "sqlite:///./inventory.db"
engine = create_engine(DATABASE_URL)
Base=declarative_base()

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    db = Session()
    try:
        yield db
    finally:
        db.close()
