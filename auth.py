# auth.py - VERSION PASSLIB SIMPLE
"""from passlib.context import CryptContext

# Utiliser des schémas plus simples qui sont inclus avec passlib
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "plaintext"],  # pbkdf2_sha256 est toujours disponible
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
"""



from passlib.context import CryptContext

# Argon2 configuration (le plus sécurisé)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,   # 64 MB
    argon2__parallelism=2,
    argon2__time_cost=3,
)

def hash_password(password: str) -> str:
    """Hash un mot de passe en utilisant Argon2."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe."""
    return pwd_context.verify(plain_password, hashed_password)