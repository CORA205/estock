from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_url="postgresql://postgres:apple@localhost:5432/efast"
engine = create_engine(db_url, echo=True)
session = sessionmaker(autocommit=False,autoflush=False, bind=engine)



def get_db():
    db = session()
    try:
        yield db # On "donne" la session à la route
    finally:
        db.close() # On la "ferme" automatiquement à la fin de la requête
