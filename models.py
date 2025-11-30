"""

from pydantic import BaseModel, field_validator
import re
from typing import Optional


# ============================================================
#  USER REGISTER
# ============================================================
class UserRegister(BaseModel):
    matricule: str
    name: str
    last_name: str
    email: str
    phone: str
    password: str

    # Matricule
    @field_validator('matricule')
    def validate_matricule(cls, v):
        v = v.strip()
        if len(v) > 15:
            raise ValueError('Le matricule ne peut pas dépasser 15 caractères')
        if not re.match(r'^[A-Za-z0-9._-]+$', v):
            raise ValueError('Le matricule peut contenir uniquement lettres, chiffres, tirets, underscores et points')
        return v

    # Téléphone (9 chiffres)
    @field_validator('phone')
    def validate_phone(cls, v):
        v = v.strip()
        if not re.fullmatch(r'\d{9}', v):
            raise ValueError('Le téléphone doit contenir exactement 9 chiffres')
        return v

    # Nom et prénom
    @field_validator('name', 'last_name')
    def validate_names(cls, v):
        v = v.strip()
        if len(v) > 255:
            raise ValueError('Le nom/prénom ne peut pas dépasser 255 caractères')
        if not re.match(r"^[A-Za-zÀ-ÿ'\-\s]+$", v):
            raise ValueError('Le nom/prénom ne peut contenir que des lettres, espaces, tirets et apostrophes')
        return v

    # Email
    @field_validator('email')
    def validate_email(cls, v):
        v = v.strip()
        if len(v) > 255:
            raise ValueError("L'email ne peut pas dépasser 255 caractères")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Format d'email invalide")
        return v

    class Config:
        extra = "forbid"



# ============================================================
#  LOGIN
# ============================================================
class UserLogin(BaseModel):
    login: str
    password: str

    class Config:
        extra = "forbid"



# ============================================================
#  REQUEST SUBMIT
# ============================================================
class RequestSubmit(BaseModel):
    all_name: str
    matricule: str
    cycle: str
    level: int
    nom_code_ue: str

    note_exam: bool = False
    note_cc: bool = False
    note_tp: bool = False
    note_tpe: bool = False
    autre: bool = False

    comment: Optional[str] = None
    just_p: bool = False

    @field_validator('all_name')
    def validate_all_name(cls, v):
        v = v.strip()
        if len(v) > 255:
            raise ValueError('Le nom complet ne peut pas dépasser 255 caractères')
        return v

    @field_validator('matricule')
    def validate_request_matricule(cls, v):
        v = v.strip()
        if len(v) > 15:
            raise ValueError('Le matricule ne peut pas dépasser 15 caractères')
        return v

    @field_validator('cycle')
    def validate_cycle(cls, v):
        v = v.strip()
        if len(v) > 50:
            raise ValueError('Le cycle ne peut pas dépasser 50 caractères')
        return v

    @field_validator('level')
    def validate_level(cls, v):
        if not isinstance(v, int) or not (0 <= v <= 32767):
            raise ValueError('Le niveau doit être un entier entre 0 et 32767')
        return v

    @field_validator('nom_code_ue')
    def validate_nom_code_ue(cls, v):
        v = v.strip()
        if len(v) > 2048:
            raise ValueError('Le nom/code UE est trop long (max 2048 caractères)')
        return v

    @field_validator('comment')
    def validate_comment(cls, v):
        if v:
            v = v.strip()
            if len(v) > 5000:
                raise ValueError('Le commentaire ne peut pas dépasser 5000 caractères')
        return v

    class Config:
        extra = "forbid"

"""







from pydantic import BaseModel, field_validator
import re
from typing import Optional


# ============================================================
#  USER REGISTER
# ============================================================
class UserRegister(BaseModel):
    matricule: str
    name: str
    last_name: str
    email: str
    phone: str
    password: str

    # Matricule
    @field_validator('matricule')
    def validate_matricule(cls, v):
        v = v.strip()
        if len(v) > 15:
            raise ValueError('Le matricule ne peut pas dépasser 15 caractères')
        if not re.match(r'^[A-Za-z0-9._-]+$', v):
            raise ValueError('Le matricule peut contenir uniquement lettres, chiffres, tirets, underscores et points')
        return v

    # Téléphone (9 chiffres)
    @field_validator('phone')
    def validate_phone(cls, v):
        v = v.strip()
        if not re.fullmatch(r'\d{9}', v):
            raise ValueError('Le téléphone doit contenir exactement 9 chiffres')
        return v

    # Nom et prénom
    @field_validator('name', 'last_name')
    def validate_names(cls, v):
        v = v.strip()
        if len(v) > 255:
            raise ValueError('Le nom/prénom ne peut pas dépasser 255 caractères')
        if not re.match(r"^[A-Za-zÀ-ÿ'\-\s]+$", v):
            raise ValueError('Le nom/prénom ne peut contenir que des lettres, espaces, tirets et apostrophes')
        return v

    # Email
    @field_validator('email')
    def validate_email(cls, v):
        v = v.strip()
        if len(v) > 255:
            raise ValueError("L'email ne peut pas dépasser 255 caractères")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Format d'email invalide")
        return v

    class Config:
        extra = "forbid"



# ============================================================
#  LOGIN
# ============================================================
class UserLogin(BaseModel):
    login: str
    password: str

    class Config:
        extra = "forbid"



# ============================================================
#  REQUEST SUBMIT
# ============================================================
class RequestSubmit(BaseModel):
    all_name: str
    matricule: str
    cycle: str
    level: int
    nom_code_ue: str

    
    state: bool = False
    
    note_exam: bool = False
    note_cc: bool = False
    note_tp: bool = False
    note_tpe: bool = False
    autre: bool = False

    comment: Optional[str] = None
    just_p: bool = False

    @field_validator('all_name')
    def validate_all_name(cls, v):
        v = v.strip()
        if len(v) > 255:
            raise ValueError('Le nom complet ne peut pas dépasser 255 caractères')
        return v

    @field_validator('matricule')
    def validate_request_matricule(cls, v):
        v = v.strip()
        if len(v) > 15:
            raise ValueError('Le matricule ne peut pas dépasser 15 caractères')
        return v

    @field_validator('cycle')
    def validate_cycle(cls, v):
        v = v.strip()
        if len(v) > 50:
            raise ValueError('Le cycle ne peut pas dépasser 50 caractères')
        return v

    @field_validator('level')
    def validate_level(cls, v):
        if not isinstance(v, int) or not (0 <= v <= 32767):
            raise ValueError('Le niveau doit être un entier entre 0 et 32767')
        return v

    @field_validator('nom_code_ue')
    def validate_nom_code_ue(cls, v):
        v = v.strip()
        if len(v) > 2048:
            raise ValueError('Le nom/code UE est trop long (max 2048 caractères)')
        return v

    @field_validator('comment')
    def validate_comment(cls, v):
        if v:
            v = v.strip()
            if len(v) > 5000:
                raise ValueError('Le commentaire ne peut pas dépasser 5000 caractères')
        return v

    class Config:
        extra = "forbid"