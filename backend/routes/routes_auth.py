# ============================================================
# routes_auth.py — Endpoints de Autenticación
# Integrante 4: Base de Datos, Seguridad y Notificaciones
# ============================================================
# Entregar al Integrante 3 para incluir en main.py de FastAPI
# ============================================================

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from auth import hash_password, verify_password, create_access_token, get_current_user, require_role
import os

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

# ── Conexión Supabase ────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")       # poner en .env
SUPABASE_KEY = os.getenv("SUPABASE_KEY")       # poner en .env
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ────────────────────────────────────────────────────────────
# MODELOS (schemas de entrada/salida)
# ────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "operador"   # valores posibles: "admin", "operador", "viewer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ConfirmPasswordRequest(BaseModel):
    """Para la doble autenticación al registrar placas."""
    password: str

# ────────────────────────────────────────────────────────────
# ENDPOINT: REGISTRAR USUARIO
# POST /api/auth/registro
# Solo un admin puede crear otros usuarios
# ────────────────────────────────────────────────────────────

@router.post("/registro", status_code=201)
def registrar_usuario(
    body: RegisterRequest,
    current_user: dict = Depends(require_role("admin"))   # solo admins
):
    # Verificar que el email no exista ya
    existente = supabase.table("usuarios").select("id").eq("email", body.email).execute()
    if existente.data:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # Guardar en Supabase con contraseña hasheada
    nuevo = supabase.table("usuarios").insert({
        "username": body.username,
        "email": body.email,
        "password_hash": hash_password(body.password),
        "role": body.role,
        "status": "activo"
    }).execute()

    return {"mensaje": "Usuario creado correctamente", "id": nuevo.data[0]["id"]}


# ────────────────────────────────────────────────────────────
# ENDPOINT: LOGIN
# POST /api/auth/login
# Devuelve token JWT
# ────────────────────────────────────────────────────────────

@router.post("/login")
def login(body: LoginRequest):
    # Buscar usuario por email
    resultado = supabase.table("usuarios").select("*").eq("email", body.email).execute()

    if not resultado.data:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    usuario = resultado.data[0]

    # Verificar contraseña
    if not verify_password(body.password, usuario["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Verificar que la cuenta esté activa
    if usuario.get("status") != "activo":
        raise HTTPException(status_code=403, detail="Cuenta inactiva o suspendida")

    # Crear token JWT con id, email y rol
    token = create_access_token(data={
        "sub": str(usuario["id"]),
        "email": usuario["email"],
        "role": usuario["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": usuario["role"],
        "username": usuario["username"]
    }


# ────────────────────────────────────────────────────────────
# ENDPOINT: DOBLE AUTENTICACIÓN AL REGISTRAR PLACAS
# POST /api/auth/confirmar-password
# El usuario debe confirmar su contraseña antes de registrar placa
# ────────────────────────────────────────────────────────────

@router.post("/confirmar-password")
def confirmar_password(
    body: ConfirmPasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    # Buscar usuario actual en BD
    resultado = supabase.table("usuarios").select("password_hash").eq("id", current_user["id"]).execute()

    if not resultado.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    password_hash = resultado.data[0]["password_hash"]

    # Verificar contraseña
    if not verify_password(body.password, password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return {"confirmado": True, "mensaje": "Contraseña confirmada. Puede registrar la placa."}


# ────────────────────────────────────────────────────────────
# ENDPOINT: VER MI PERFIL (ejemplo de ruta protegida)
# GET /api/auth/perfil
# ────────────────────────────────────────────────────────────

@router.get("/perfil")
def ver_perfil(current_user: dict = Depends(get_current_user)):
    resultado = supabase.table("usuarios").select("id, username, email, role, status, created_at") \
        .eq("id", current_user["id"]).execute()
    return resultado.data[0]
