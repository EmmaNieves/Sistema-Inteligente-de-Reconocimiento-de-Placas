# 🤖 TRASPASO COMPLETO — PlacaControl
> Pega esto en el chat de la IA para que sepa todo el contexto del proyecto.
> Las claves reales están en los archivos .env (NO se suben al repo).

---

## PROYECTO
- **Nombre:** PlacaControl — Sistema Inteligente de Reconocimiento de Placas
- **Repo:** https://github.com/EmmaNieves/Sistema-Inteligente-de-Reconocimiento-de-Placas
- **Rama activa:** `main`

---

## STACK COMPLETO

### Backend (Python — carpeta `backend/`)
- **FastAPI** + **Uvicorn** → API REST en puerto **8000**
- **YOLO** (ultralytics) + **PaddleOCR** → detección y OCR de placas
- **Supabase** → base de datos en la nube (PostgreSQL)
- **CallMeBot** → notificaciones WhatsApp gratuitas (sin cuenta Meta)
- **python-dotenv** → variables desde `backend/.env`
- **JWT** (python-jose) + **bcrypt** (passlib) → autenticación

### Frontend (Node.js/TypeScript — carpeta `frontend-dashboard/`)
- **Express** + **Vite** + **React** → servidor único en puerto **5000**
- **Tailwind CSS** + **shadcn/ui** + **Recharts** → UI del dashboard
- **Supabase JS** → acceso a BD desde Express
- Corre con: `npm run dev` desde `frontend-dashboard/`

---

## ARCHIVOS CLAVE

```
backend/
  api.py                      ← entrada FastAPI (tiene load_dotenv() al inicio)
  auth.py                     ← JWT con SECRET_KEY desde os.getenv("JWT_SECRET")
  database.py                 ← lógica Supabase completa
  processor.py                ← YOLO + PaddleOCR
  whatsapp_notifications.py   ← CallMeBot (WHATSAPP_NUMBER_1/2 + CALLMEBOT_APIKEY_1/2)
  test_whatsapp.py            ← prueba directa: python test_whatsapp.py
  test_deteccion_alerta.py    ← simula detección real y dispara WhatsApp
  routes/
    detections.py             ← llama alerta_placa_no_registrada() si no autorizada
    alerts.py                 ← GET /alerts, PATCH resolve, GET /count
    vehicles.py               ← CRUD vehículos
    cameras.py                ← CRUD cámaras
    routes_auth.py            ← /api/auth/login, /registro, /perfil
    simulador.py              ← simulaciones
    dashboard.py              ← stats generales

frontend-dashboard/
  server/index.ts             ← Express (host: localhost, puerto 5000)
  server/routes.ts            ← endpoints + makeToken incluye rol en JWT
                                 DELETE /vehicles/:id borra plates antes de borrar vehiculo
  server/middleware/auth.ts   ← verifica JWT y rol
  server/supabase.ts          ← cliente con service_role key
  client/src/pages/Estadisticas.tsx  ← botón "Exportar CSV" funcional (UTF-8 BOM)
  client/src/lib/api.ts       ← todas las llamadas al backend
```

---

## VARIABLES DE ENTORNO NECESARIAS

### `backend/.env`
```
SUPABASE_URL=https://ecwomhimxcypilnuatdn.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjd29taGlteGN5cGlsbnVhdGRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcwNzM0MTAsImV4cCI6MjA5MjY0OTQxMH0.uqHcrfBjNTNXaRNbD-BlO6dv6HjmNXnCd9buA9Rn-1w
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjd29taGlteGN5cGlsbnVhdGRuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzA3MzQxMCwiZXhwIjoyMDkyNjQ5NDEwfQ.ms4i4gRlYIdJOnxIaUkLxDspmPIbZmg1Y5iXcUXFI3I
SUPABASE_STORAGE_BUCKET=plate-images
SUPABASE_STORAGE_BUCKET=plate-images
JWT_SECRET=/uE/ZUYTe3w5j0hE9+e5yUMWWpzgAEpVS36k/unYR5Yzau0QR/OPosTWCtMn9LNphUTXvrFVAtg/QEnu9J5bpg==
WHATSAPP_NUMBER_1=573243333381
CALLMEBOT_APIKEY_1=2995336
WHATSAPP_NUMBER_2=573332487255
CALLMEBOT_APIKEY_2=<pendiente — número 2 debe activar CallMeBot>
```

### `frontend-dashboard/.env`
```
SUPABASE_URL=https://ecwomhimxcypilnuatdn.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjd29taGlteGN5cGlsbnVhdGRuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzA3MzQxMCwiZXhwIjoyMDkyNjQ5NDEwfQ.ms4i4gRlYIdJOnxIaUkLxDspmPIbZmg1Y5iXcUXFI3I
JWT_SECRET=mi_clave_super_secreta_2024
```

> ⚠️ JWT_SECRET debe ser IGUAL en los dos .env

---

## TABLAS SUPABASE
- `users` → id, username, email, password_hash, role, status
- `vehicles` → id, plate, owner, vehicle_type, observations, registered_by, created_at
- `plates` → id, plate_text, camera_id, vehicle_id, yolo/ocr_confidence, authorized, image_url, detection_timestamp
- `alertas` → id, plate_id, camera_id, plate_text, estado_envio, resolved, fecha
- `cameras` → id, camera_code, name, location, status, active, latitud, longitud
- `simulations` → id, camera_code, city, plate_text, vehicle_type, authorized

---

## FLUJO DE DETECCIÓN
1. Cliente → `POST /detections/detect` con imagen
2. YOLO detecta placa → PaddleOCR lee texto
3. Busca en tabla `vehicles` → ¿registrada?
4. Guarda en `plates` con authorized=true/false
5. Si NO autorizada → crea alerta en `alertas` + **WhatsApp via CallMeBot**
6. Responde JSON

---

## FIXES REALIZADOS
1. `backend/api.py` → `load_dotenv()` al inicio antes de imports
2. `backend/auth.py` → `SECRET_KEY` desde `os.getenv("JWT_SECRET")`
3. `frontend-dashboard/server/index.ts` → `host: "localhost"` (no `0.0.0.0`, Windows no lo soporta)
4. `frontend-dashboard/server/routes.ts` → `makeToken(userId, role)` incluye rol en JWT
5. `frontend-dashboard/server/routes.ts` → DELETE vehicles borra primero en `plates` (FK constraint)
6. `backend/whatsapp_notifications.py` → migrado a **CallMeBot** (gratuito, sin Meta)
7. `backend/routes/detections.py` → conectado `alerta_placa_no_registrada()` al flujo
8. `Estadisticas.tsx` → botón CSV exporta datos reales con UTF-8 BOM

---

## PENDIENTES
- [ ] Activar CallMeBot para número 2 (573332487255) → agregar CALLMEBOT_APIKEY_2
- [ ] Verificar restricciones del prompt del profesor (ver PDF de rúbrica)
- [ ] Asegurar min 5 commits por integrante en el historial

## CUENTAS CON COMMITS
- `EmmaNieves` — cuenta principal del repo
- `JhonFMin` — fixes de WhatsApp, CSV, bat de inicio
- `gomezyeleinis9-hue` — diagnóstico, alertas, documentación

## PARA ARRANCAR EL PROYECTO
Ejecutar `INICIAR.bat` en la raíz del proyecto (doble clic o como administrador).
