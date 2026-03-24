from fastapi import APIRouter, HTTPException, Depends

from database.database import engine, get_db
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from schemas.models import  UserCreate, UserLogin
from utils.auth import hash_password, verify_password, create_access_token

from models import database_models



secu = APIRouter(prefix="/users")


database_models.Base.metadata.create_all(bind=engine)




@secu.post("/register")
def register(ids: UserCreate):
    with Session(engine) as session:
        session.add(database_models.User(**ids.model_dump()))
        session.commit()

    return "Nouvel utilisateur ajouté"


@secu.get("/login")
def login(user: str, pwd: str):
    with Session(engine) as session:
        stmt = select(database_models.User).where(
            and_(
                database_models.User.username == user,
                database_models.User.password == pwd
            )
        )
        ids = session.scalar(stmt)

        if not ids:
            raise HTTPException(status_code=401, detail={"Identifiants incorrects"})

        return "Login réussi"


@secu.get("/all_users")
def all_users():
    with Session(engine) as session:
        users = session.query(database_models.User).all()
        return users










@secu.post("/register_crypt")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. On hache le mot de passe
    hashed_pwd = hash_password(user_in.password)

    # 2. On crée l'entrée en base (Note : on utilise hashed_password)
    new_user = database_models.User(
        username=user_in.username,
        hashed_password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Utilisateur créé", "id": new_user.id}




@secu.post("/login_verify")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    # 1. On récupère l'user par son username
    user = db.query(database_models.User).filter(
        database_models.User.username == user_in.username
    ).first()

    # 2. Vérification double (existence + hash)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")

    # 3. Si c'est OK, on génère le badge (Token)
    token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}
