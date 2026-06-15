# ============================================================
# auth.py — Módulo de Autenticación
# Integrante 4: Base de Datos, Seguridad y Notificaciones
# ============================================================
# Entregar al Integrante 3 (Backend FastAPI)
# ============================================================

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# ── Configuración JWT ────────────────────────────────────────
SECRET_KEY = "CAMBIA_ESTO_POR_UNA_CLAVE_SEGURA_LARGA"  # ⚠️ cambiar en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ── Hash de contraseñas ──────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ────────────────────────────────────────────────────────────
# FUNCIONES DE CONTRASEÑA
# ────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano a hash bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash guardado."""
    return pwd_context.verify(plain_password, hashed_password)

# ────────────────────────────────────────────────────────────
# FUNCIONES JWT
# ────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT con los datos del usuario."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decodifica y valida un token JWT. Lanza excepción si es inválido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ────────────────────────────────────────────────────────────
# DEPENDENCIAS DE RUTA (para proteger endpoints)
# ────────────────────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependencia que extrae el usuario del token JWT.
    Uso: agregar `current_user: dict = Depends(get_current_user)` en el endpoint.
    """
    payload = decode_token(token)
    user_id = payload.get("sub")
    role = payload.get("role")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token sin usuario")
    return {"id": user_id, "role": role, "email": payload.get("email")}

def require_role(*roles: str):
    """
    Dependencia de rol. Uso:
        Depends(require_role("admin"))
        Depends(require_role("admin", "operador"))
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere rol: {', '.join(roles)}"
            )
        return current_user
    return role_checker
