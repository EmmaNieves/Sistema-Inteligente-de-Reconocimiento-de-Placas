# 🚗 PlacaControl — Sistema Inteligente de Reconocimiento de Placas

Sistema de visión artificial que detecta y reconoce placas vehiculares colombianas en tiempo real usando **YOLOv8 + PaddleOCR**, con una **API REST en FastAPI**, base de datos en **Supabase**, dashboard web en **React/TypeScript** y **alertas automáticas por WhatsApp**.

---

## 📋 Descripción del problema que resuelve

El control vehicular manual en parqueaderos, conjuntos residenciales y zonas de acceso restringido es lento, propenso a errores humanos y no escala. **PlacaControl** automatiza ese proceso: una cámara captura el vehículo, el sistema detecta la placa con IA, la compara contra una lista de autorizados en la base de datos y, si no está registrada, envía una alerta inmediata por WhatsApp al administrador. Todo queda registrado con timestamp e imagen en la nube.

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend API | FastAPI + Uvicorn |
| Detección | YOLOv8 (modelo entrenado para placas colombianas) |
| OCR | PaddleOCR |
| Base de datos | Supabase (PostgreSQL en la nube) |
| Almacenamiento de imágenes | Supabase Storage |
| Autenticación | JWT (python-jose + passlib/bcrypt) |
| Alertas | WhatsApp Business API (Meta) |
| Frontend | React + TypeScript + Tailwind CSS |
| Variables de entorno | python-dotenv |

---

## 📁 Estructura del proyecto

```
├── backend/
│   ├── api.py                    ← FastAPI principal (registra todos los routers)
│   ├── database.py               ← Funciones de Supabase (detecciones, vehículos, alertas)
│   ├── processor.py              ← YOLO + PaddleOCR (detección e interpretación de placa)
│   ├── auth.py                   ← JWT: hash, tokens, dependencias de ruta
│   ├── whatsapp_notifications.py ← Alertas WhatsApp a múltiples números
│   └── routes/
│       ├── detections.py         ← POST /detections/detect  GET /detections/
│       ├── vehicles.py           ← CRUD /vehicles/
│       ├── alerts.py             ← GET/PATCH /alerts/
│       ├── cameras.py            ← GET/POST /cameras/
│       ├── stats.py              ← GET /stats/
│       ├── dashboard.py          ← GET /dashboard/
│       ├── simulador.py          ← POST /simulate/
│       └── routes_auth.py        ← POST /api/auth/login  /registro  /perfil
│
├── frontend-dashboard/           ← React + TypeScript + Tailwind
│   ├── client/src/pages/         ← Dashboard, Detecciones, Vehículos, Alertas, etc.
│   └── server/                   ← Servidor de desarrollo
│
├── simulador.py                  ← Script para simular detecciones en masa
├── requirements.txt              ← Dependencias Python del backend
└── README.md
```

---

## ⚙️ Instalación y ejecución

### Requisitos previos
- Python 3.9+
- Node.js 18+
- Cuenta en [Supabase](https://supabase.com) (gratis)
- Cuenta en [Meta for Developers](https://developers.facebook.com) para WhatsApp Business API

### 1. Clonar el repositorio

```bash
git clone https://github.com/EmmaNieves/Sistema-Inteligente-de-Reconocimiento-de-Placas.git
cd Sistema-Inteligente-de-Reconocimiento-de-Placas
git checkout main
```

### 2. Configurar variables de entorno

Crea el archivo `backend/.env` con tus credenciales:

```env
# Supabase
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=tu_anon_key_aqui
SUPABASE_SERVICE_KEY=tu_service_role_key_aqui
SUPABASE_STORAGE_BUCKET=plate-images

# WhatsApp Business API (Meta)
WHATSAPP_TOKEN=tu_token_de_meta_aqui
PHONE_NUMBER_ID=tu_phone_number_id_aqui

# Números que recibirán las alertas (con código de país, sin +)
WHATSAPP_NUMBER_1=573243333381
WHATSAPP_NUMBER_2=573332487255
```

> ⚠️ **Nunca subas el archivo `.env` al repositorio.** Ya está en `.gitignore`.

### 3. Instalar dependencias Python

```bash
cd backend
pip install -r ../requirements.txt
```

### 4. Levantar el backend

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Accede a la documentación Swagger en: **http://localhost:8000/docs**

### 5. Levantar el frontend

```bash
cd frontend-dashboard
npm install
npm run dev
```

Accede al dashboard en: **http://localhost:3000**

### 6. (Opcional) Ejecutar el simulador de placas

```bash
# Desde la raíz del proyecto (con el backend corriendo)
python simulador.py
```

---

## 🔌 Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Estado del sistema |
| POST | `/detections/detect` | Recibe imagen, detecta placa y guarda resultado |
| GET | `/detections/` | Lista todas las detecciones |
| GET | `/vehicles/` | Lista vehículos autorizados |
| POST | `/vehicles/` | Registra un vehículo autorizado |
| DELETE | `/vehicles/{plate}` | Elimina un vehículo autorizado |
| GET | `/vehicles/check/{plate}` | Verifica si una placa está autorizada |
| GET | `/alerts/` | Lista alertas de acceso no autorizado |
| PATCH | `/alerts/{id}/resolve` | Marca una alerta como resuelta |
| GET | `/cameras/` | Lista cámaras registradas |
| POST | `/cameras/` | Registra una nueva cámara |
| GET | `/stats/` | Estadísticas generales del sistema |
| GET | `/dashboard/` | Resumen completo para el dashboard |
| POST | `/simulate/` | Simula una detección (para pruebas) |
| POST | `/api/auth/login` | Login y obtención de token JWT |
| GET | `/api/auth/perfil` | Ver perfil del usuario autenticado |

---

## 🔄 Flujo de detección

```
Imagen (cámara) 
    → POST /detections/detect
    → YOLO detecta región de la placa
    → PaddleOCR lee los caracteres
    → corregir_placa() normaliza el texto (formato ABC123)
    → is_authorized_plate() consulta tabla vehicles en Supabase
    → save_detection() guarda en tabla plates
    → Si NO autorizada → create_alert() + alerta WhatsApp a los admins
    → Respuesta JSON con resultado
```

---

## 🤖 Uso de IA

Este proyecto utilizó las siguientes herramientas de IA durante su desarrollo:

- **Claude (Anthropic):** Apoyo en la arquitectura del sistema, diseño de la API REST, limpieza y organización del código, generación del README y configuración del sistema de alertas WhatsApp con múltiples destinatarios.
- **YOLOv8 (Ultralytics):** Modelo de visión artificial entrenado para localizar la región de la placa dentro de la imagen capturada por la cámara.
- **PaddleOCR:** Motor de reconocimiento óptico de caracteres que lee el texto de la placa recortada y lo convierte en string.

---

## 👥 Integrantes del grupo

- [NOMBRE INTEGRANTE 1]
- [NOMBRE INTEGRANTE 2]
- [NOMBRE INTEGRANTE 3]
- [NOMBRE INTEGRANTE 4]

---

## 🎓 Información académica

**Materia:** Programación Avanzada  
**Universidad:** Universidad de La Guajira  
**Docente:** Eduardo Sierra  
**Período:** 2026-I
