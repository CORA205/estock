import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt

# Configurations JWT
SECRET_KEY = "09d25e094faa6ca2556g818166b7a9563b93z7099f6f0f4caa6cf63b58e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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

