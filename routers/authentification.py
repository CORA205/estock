from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select

from database.database import engine, get_db
from sqlalchemy.orm import Session
from schemas.models import  UserCreate, UserLogin, RoleCreate
from utils.auth import hash_password, verify_password, create_access_token, require_superadmin, get_current_user


from models import database_models



secu = APIRouter(prefix="/users", tags=["Users & Auth"])



# @secu.post("/register")
# def register(user_in: UserCreate, db: Session = Depends(get_db)):
#     # 1. On hache le mot de passe
#     hashed_pwd = hash_password(user_in.password)
#
#     # 2. On crée l'entrée en base (Note : on utilise hashed_password)
#     new_user = database_models.User(
#         username=user_in.username,
#         hashed_password=hashed_pwd
#     )
#
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return {"message": "Utilisateur créé", "id": new_user.id}




@secu.post("/login")
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







# ─────────────────────────────────────────────
# PUBLIC
# ─────────────────────────────────────────────

@secu.get("/me")
def get_me(current_user=Depends(get_current_user)):
    """L'utilisateur connecté consulte son propre profil."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role_id": current_user.role_id
    }


# SUPERADMIN ONLY

@secu.get("/admin/all", dependencies=[Depends(require_superadmin)])
def all_users(db: Session = Depends(get_db)):
    """Liste tous les utilisateurs."""
    return db.scalars(select(database_models.User)).all()


@secu.post("/admin/create-user", dependencies=[Depends(require_superadmin)], status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Crée un utilisateur et lui attribue un rôle directement."""
    existing = db.scalars(
        select(database_models.User).where(database_models.User.username == user_in.username)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ce nom d'utilisateur existe déjà")

    # Vérifier que le rôle existe si fourni
    if user_in.role_id:
        role = db.get(database_models.Role, user_in.role_id)
        if not role:
            raise HTTPException(status_code=404, detail=f"Rôle {user_in.role_id} introuvable")

    new_user = database_models.User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
        role_id=user_in.role_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Utilisateur créé", "id": new_user.id, "role_id": new_user.role_id}


@secu.patch("/admin/{id}/assign-role", dependencies=[Depends(require_superadmin)])
def assign_role(id: int, role_id: int, db: Session = Depends(get_db)):
    """Attribue ou modifie le rôle d'un utilisateur existant."""
    user = db.get(database_models.User, id)
    if not user:
        raise HTTPException(status_code=404, detail=f"Utilisateur {id} introuvable")

    role = db.get(database_models.Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Rôle {role_id} introuvable")

    user.role_id = role_id
    db.commit()
    db.refresh(user)
    return {"message": f"Rôle '{role.name}' attribué à '{user.username}'"}


@secu.delete("/admin/{id}", dependencies=[Depends(require_superadmin)])
def delete_user(id: int, db: Session = Depends(get_db)):
    """Supprime un utilisateur."""
    user = db.get(database_models.User, id)
    if not user:
        raise HTTPException(status_code=404, detail=f"Utilisateur {id} introuvable")

    db.delete(user)
    db.commit()
    return {"detail": f"Utilisateur {id} supprimé"}


# GESTION DES ROLES (superadmin only)

@secu.get("/admin/roles", dependencies=[Depends(require_superadmin)])
def all_roles(db: Session = Depends(get_db)):
    return db.scalars(select(database_models.Role)).all()


@secu.post("/admin/roles", dependencies=[Depends(require_superadmin)], status_code=201)
def create_role(role_in: RoleCreate, db: Session = Depends(get_db)):
    existing = db.scalars(
        select(database_models.Role).where(database_models.Role.name == role_in.name)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ce rôle existe déjà")

    new_role = database_models.Role(name=role_in.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@secu.delete("/admin/roles/{id}", dependencies=[Depends(require_superadmin)])
def delete_role(id: int, db: Session = Depends(get_db)):
    role = db.get(database_models.Role, id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Rôle {id} introuvable")

    db.delete(role)
    db.commit()
    return {"detail": f"Rôle {id} supprimé"}