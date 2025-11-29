# auth.py - VERSION PASSLIB SIMPLE
from passlib.context import CryptContext

# Utiliser des schémas plus simples qui sont inclus avec passlib
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "plaintext"],  # pbkdf2_sha256 est toujours disponible
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)