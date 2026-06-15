// ═══════════════════════════════════════════════════════════════════════════════
// frontend-dashboard/server/middleware/auth.ts
// Middleware de autenticación JWT con soporte de roles
// ═══════════════════════════════════════════════════════════════════════════════

import { Request, Response } from "express";
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET || "your-secret-key-change-this";

// ─── Tipos ──────────────────────────────────────────────────────────────────
export interface AuthUser {
  id: string;
  email: string;
  role: "administrador" | "operador" | "visualizador";
}

export interface AuthRequest extends Request {
  user?: AuthUser;
}

// ─── Roles y permisos ──────────────────────────────────────────────────────
// Jerarquía: administrador > operador > visualizador
const ROLE_HIERARCHY: Record<string, number> = {
  administrador: 3,
  operador: 2,
  visualizador: 1,
};

// ─── Función: Verificar JWT y extraer usuario ──────────────────────────────
export async function requireAuth(
  req: AuthRequest,
  res: Response
): Promise<AuthUser | null> {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader?.startsWith("Bearer ")) {
      res.status(401).json({ detail: "Token no proporcionado" });
      return null;
    }

    const token = authHeader.slice(7);
    const decoded = jwt.verify(token, JWT_SECRET) as AuthUser;
    req.user = decoded;
    return decoded;
  } catch (err) {
    res.status(401).json({ detail: "Token inválido o expirado" });
    return null;
  }
}

// ─── Función: Verificar rol mínimo requerido ────────────────────────────────
export async function requireRole(
  req: AuthRequest,
  res: Response,
  minRole: "visualizador" | "operador" | "administrador"
): Promise<AuthUser | null> {
  const user = await requireAuth(req, res);
  if (!user) return null;

  const userRank = ROLE_HIERARCHY[user.role] ?? 0;
  const minRank = ROLE_HIERARCHY[minRole] ?? 0;

  if (userRank < minRank) {
    res.status(403).json({
      detail: `Acceso denegado. Se requiere rol '${minRole}' o superior. Tu rol es '${user.role}'.`,
    });
    return null;
  }

  return user;
}

// ─── Función: Generar token JWT ─────────────────────────────────────────────
export function generateToken(user: AuthUser): string {
  return jwt.sign(user, JWT_SECRET, { expiresIn: "7d" });
}

// ─── Middleware Express (opcional) ──────────────────────────────────────────
export function authMiddleware(
  req: AuthRequest,
  res: Response,
  next: Function
) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith("Bearer ")) {
    return res.status(401).json({ detail: "Token no proporcionado" });
  }

  try {
    const token = authHeader.slice(7);
    const decoded = jwt.verify(token, JWT_SECRET) as AuthUser;
    req.user = decoded;
    next();
  } catch (err) {
    res.status(401).json({ detail: "Token inválido o expirado" });
  }
}

// ─── Funciones helper: Validar acceso por rol ──────────────────────────────
export function canRead(userRole: string): boolean {
  return ROLE_HIERARCHY[userRole] >= ROLE_HIERARCHY["visualizador"];
}

export function canWrite(userRole: string): boolean {
  return ROLE_HIERARCHY[userRole] >= ROLE_HIERARCHY["operador"];
}

export function canAdmin(userRole: string): boolean {
  return ROLE_HIERARCHY[userRole] >= ROLE_HIERARCHY["administrador"];
}
