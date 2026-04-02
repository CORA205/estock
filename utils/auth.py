import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from database.database import get_db
from models import database_models

from fastapi.security import HTTPBasic, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

#Config super_admin
SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME", "superadmin")

# Configurations JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
security = HTTPBearer()

# --- BCRYPT ---

def hash_password(password: str) -> str:
    """Hache un mot de passe en utilisant directement la lib bcrypt."""
    # 1. Convertir le string en bytes (UTF-8)
    pwd_bytes = password.encode('utf-8')
    # 2. Générer un sel aléatoire
    salt = bcrypt.gensalt()
    # 3. Hacher
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    # 4. Retourner en string pour le stockage en base Postgres
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie le mot de passe en comparant les bytes."""
    password_byte = plain_password.encode('utf-8')
    hashed_byte = hashed_password.encode('utf-8')
    # bcrypt.checkpw compare les deux et gère la sécurité temporelle
    return bcrypt.checkpw(password_byte, hashed_byte)

# ---FONCTION JWT---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# Fonctions securite user et super_admin

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = db.get(database_models.User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    return user

def require_superadmin(current_user = Depends(get_current_user)):
    if current_user.username != SUPERADMIN_USERNAME:
        raise HTTPException(status_code=403, detail="Accès réservé au superadmin")
    return current_user


######

def require_admin(current_user = Depends(get_current_user)):
    if not current_user.role == "Admin":
        raise HTTPException(status_code=403, detail="Vous n'avez pas l'autorisation requise")
    return current_user




#
# ROLE_HIERARCHY = {
#     "employee": 1,
#     "manager":  2,
#     "admin":    3,
# }


#
# def require_role(minimum_role: str):
#     """
#     Vérifie que l'utilisateur a au moins le niveau requis.
#
#     require_role("employee") → employee, manager, admin ✅
#     require_role("manager")  → manager, admin ✅ — employee ❌
#     require_role("admin")    → admin ✅ — manager, employee ❌
#     """
#     def checker(current_user=Depends(get_current_user)):
#         if not current_user.role:
#             raise HTTPException(status_code=403, detail="Aucun rôle attribué")
#
#         user_level = ROLE_HIERARCHY.get(current_user.role.name, 0)
#         required_level = ROLE_HIERARCHY.get(minimum_role, 99)
#
#         if user_level < required_level:
#             raise HTTPException(status_code=403, detail="Accès non autorisé")
#
#         return current_user
#     return checker