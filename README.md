# Sistema Inteligente de Reconocimiento de Placas - PlacaControl

**Universidad de La Guajira - Facultad de Ingenieria - Programacion Avanzada 2026-I**  
**Proyecto:** LPR Smart City para deteccion, validacion y analisis de placas vehiculares.

## Descripcion General

PlacaControl es un sistema inteligente para reconocer placas vehiculares colombianas usando vision por computadora. El proyecto combina un backend en Python con FastAPI, un modelo YOLO entrenado para detectar placas, PaddleOCR para leer los caracteres, Supabase como base de datos y almacenamiento, y un dashboard web en React/TypeScript para administrar vehiculos, camaras, detecciones, alertas, estadisticas y audiencias.

El sistema permite capturar una imagen desde una camara, detectar la placa, validar si pertenece a un vehiculo autorizado, registrar la deteccion en la nube y generar alertas automaticas cuando la placa no esta registrada.

## Problema Que Resuelve

En ciudades intermedias como Riohacha, conjuntos residenciales, parqueaderos, edificios y zonas comerciales suelen depender de controles manuales para registrar vehiculos. Esto genera errores humanos, demoras, poca trazabilidad y ausencia de datos utiles para tomar decisiones de seguridad, movilidad o negocio.

PlacaControl automatiza este proceso con camaras de bajo costo y analisis inteligente:

- Control de acceso a conjuntos, edificios o parqueaderos.
- Deteccion de vehiculos no autorizados.
- Registro historico de placas, hora, camara e imagen.
- Alertas en tiempo real por WhatsApp.
- Estadisticas de flujo vehicular por hora, tipo de vehiculo y camara.
- Perfilamiento de audiencias por recurrencia, zona y valor estimado del vehiculo.
- Visualizacion de camaras y actividad en mapa.

## Integrantes

| Nombre | Rol principal |
| --- | --- |
| Emmanuel Enrique Nieves Carrillo | Backend Python, YOLO, OCR y arquitectura del sistema |
| Jhonar David De Arco Mindiola | Backend Node.js/Express, endpoints de estadisticas y audiencias |
| Jhon Faber Mindiola Atencio | Frontend React, dashboard y visualizaciones |
| Yeleinys Yanith Gomez Jimenez | Frontend React, UI/UX e integracion con Supabase |

## Stack Tecnologico

| Capa | Tecnologia |
| --- | --- |
| Vision por computadora | YOLOv8, Ultralytics |
| OCR | PaddleOCR, PaddlePaddle |
| Backend de deteccion | Python, FastAPI, Uvicorn, OpenCV |
| Backend web/dashboard | Node.js, Express, TypeScript |
| Frontend | React, Vite, TypeScript |
| UI | Tailwind CSS, shadcn/ui, Radix UI |
| Graficas | Recharts |
| Mapas | Leaflet, React Leaflet |
| Base de datos | Supabase PostgreSQL |
| Storage | Supabase Storage |
| Autenticacion | JWT, bcrypt/bcryptjs |
| Notificaciones | CallMeBot para WhatsApp |
| Variables de entorno | python-dotenv, dotenv |

## Arquitectura

```text
Camara / imagen / simulador
        |
        | POST /detections/detect
        v
Backend Python FastAPI
        |
        | YOLO detecta la region de la placa
        | PaddleOCR lee el texto
        | Se normaliza el formato de placa
        v
Supabase PostgreSQL + Storage
        |
        | Guarda detecciones, imagenes, camaras, vehiculos y alertas
        v
Backend Node.js / Express
        |
        | Sirve endpoints del dashboard:
        | auth, dashboard, estadisticas, audiencias,
        | detecciones, alertas, vehiculos, camaras y usuarios
        v
Frontend React
        |
        | Dashboard, Detecciones, Alertas, Estadisticas,
        | Audiencias, Mapa, Camaras, Vehiculos y Usuarios
```

## Funcionalidades Principales

- Deteccion automatica de placas con YOLOv8.
- Lectura OCR de placas con PaddleOCR.
- Correccion del texto detectado al formato colombiano `ABC123`.
- Validacion de placas contra la tabla de vehiculos autorizados.
- Registro de detecciones en Supabase.
- Carga de imagenes al bucket `plate-images`.
- Creacion de alertas para placas no autorizadas.
- Envio de alertas por WhatsApp mediante CallMeBot.
- Dashboard protegido con login y JWT.
- Roles de usuario: administrador, operador y visualizador.
- CRUD de vehiculos autorizados.
- CRUD de camaras.
- Modulo de detecciones con filtros.
- Modulo de alertas con resolucion.
- Modulo de estadisticas con trafico por hora, heatmap, confianza OCR y categorias.
- Modulo de audiencias con clasificacion Residente, Visitante y Transito.
- Estimacion de modelo y precio del vehiculo para analisis comercial.
- Mapa interactivo con ubicacion de camaras.
- Simulador de flujo vehicular para pruebas.

## Estructura Del Proyecto

```text
proyecto_placa/
├── README.md
├── TRASPASO_IA.md
├── requirements.txt
├── placas.yaml
├── simulador.py
├── INICIAR.bat
├── backend/
│   ├── api.py
│   ├── auth.py
│   ├── database.py
│   ├── processor.py
│   ├── whatsapp_notifications.py
│   ├── test_whatsapp.py
│   ├── test_deteccion_alerta.py
│   ├── routes/
│   │   ├── alerts.py
│   │   ├── cameras.py
│   │   ├── dashboard.py
│   │   ├── detections.py
│   │   ├── routes_auth.py
│   │   ├── simulador.py
│   │   ├── stats.py
│   │   └── vehicles.py
│   └── runs/detect/train-5/
│       ├── results.csv
│       ├── results.png
│       └── weights/
│           ├── best.pt
│           └── last.pt
└── frontend-dashboard/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── client/
    │   ├── index.html
    │   └── src/
    │       ├── App.tsx
    │       ├── main.tsx
    │       ├── components/
    │       ├── hooks/
    │       ├── lib/
    │       └── pages/
    ├── server/
    │   ├── index.ts
    │   ├── routes.ts
    │   ├── supabase.ts
    │   ├── storage.ts
    │   ├── static.ts
    │   ├── vite.ts
    │   └── middleware/auth.ts
    ├── shared/
    │   └── schema.ts
    └── script/
        ├── build.ts
        └── make-zip.mjs
```

## Archivos Clave

| Archivo | Funcion |
| --- | --- |
| `backend/api.py` | Entrada principal de FastAPI y registro de routers |
| `backend/processor.py` | Carga YOLO y PaddleOCR; detecta y corrige placas |
| `backend/database.py` | Acceso a Supabase, storage, vehiculos, detecciones, camaras y alertas |
| `backend/whatsapp_notifications.py` | Envio de mensajes por WhatsApp usando CallMeBot |
| `backend/routes/detections.py` | Endpoint para recibir imagenes, detectar placas y disparar alertas |
| `frontend-dashboard/server/index.ts` | Servidor Express/Vite del dashboard |
| `frontend-dashboard/server/routes.ts` | API del dashboard: auth, estadisticas, audiencias, CRUDs y simulaciones |
| `frontend-dashboard/server/middleware/auth.ts` | Middleware de autenticacion y roles |
| `frontend-dashboard/client/src/App.tsx` | Rutas protegidas del frontend |
| `frontend-dashboard/client/src/lib/api.ts` | Cliente HTTP usado por las paginas React |
| `INICIAR.bat` | Script de arranque para Windows |

## Requisitos Previos

- Python 3.11 recomendado.
- Node.js 18 o superior.
- npm.
- Cuenta en Supabase.
- Bucket de Supabase Storage llamado `plate-images`.
- Modelo YOLO en `backend/runs/detect/train-5/weights/best.pt`.
- Conexion a internet para Supabase y CallMeBot.

## Variables De Entorno

No se deben subir credenciales reales al repositorio. Crear los archivos `.env` localmente.

### `backend/.env`

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key
SUPABASE_SERVICE_KEY=tu_service_role_key
SUPABASE_STORAGE_BUCKET=plate-images

JWT_SECRET=un_secreto_largo_y_seguro

WHATSAPP_NUMBER_1=57XXXXXXXXXX
CALLMEBOT_APIKEY_1=tu_apikey_1
WHATSAPP_NUMBER_2=57XXXXXXXXXX
CALLMEBOT_APIKEY_2=tu_apikey_2
```

### `frontend-dashboard/.env`

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_KEY=tu_service_role_key
JWT_SECRET=el_mismo_secreto_usado_en_el_backend_si_aplica
```

### Nota De Seguridad

- Usar `SUPABASE_SERVICE_KEY` solo en backend o servidor, nunca exponerla en un cliente publico.
- Mantener `.env` fuera de Git.
- Rotar las llaves si alguna credencial real fue compartida accidentalmente.
- Usar un `JWT_SECRET` largo, unico y privado.

## Instalacion Manual

### 1. Clonar El Repositorio

```bash
git clone https://github.com/EmmaNieves/Sistema-Inteligente-de-Reconocimiento-de-Placas.git
cd Sistema-Inteligente-de-Reconocimiento-de-Placas
```

### 2. Preparar Backend Python

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crear `backend/.env` con las variables indicadas arriba.

Ejecutar FastAPI:

```bash
cd backend
uvicorn api:app --reload --host localhost --port 8000
```

Backend disponible en:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### 3. Preparar Frontend Y Servidor Express

```bash
cd frontend-dashboard
npm install
npm run dev
```

Dashboard disponible en:

- Frontend/Express: `http://localhost:5000`

## Arranque Automatico En Windows

El proyecto incluye `INICIAR.bat` en la raiz. Este script:

1. Crea variables de entorno locales.
2. Crea o activa el entorno virtual de Python.
3. Instala dependencias Python.
4. Instala dependencias Node si no existen.
5. Libera los puertos `8000` y `5000`.
6. Inicia backend y frontend en ventanas separadas.
7. Abre `http://localhost:5000`.

Uso:

```bat
INICIAR.bat
```

## Flujo De Deteccion

1. Una camara, imagen o simulador envia una imagen a `POST /detections/detect`.
2. `processor.py` carga el modelo YOLO desde `backend/runs/detect/train-5/weights/best.pt`.
3. YOLO detecta la region donde esta la placa.
4. OpenCV recorta y mejora la imagen.
5. PaddleOCR lee el texto de la placa.
6. `corregir_placa()` limpia y normaliza el resultado al formato `ABC123`.
7. El backend consulta Supabase para saber si la placa existe en `vehicles`.
8. Se guarda la deteccion en `plates`, con confianza YOLO/OCR, camara, estado e imagen.
9. Si la placa no esta autorizada, se crea una alerta en `alertas`.
10. Se envia notificacion por WhatsApp mediante CallMeBot.
11. El frontend consume los datos y actualiza dashboard, alertas, estadisticas y audiencias.

## Endpoints Principales

### Backend Python - FastAPI `http://localhost:8000`

| Metodo | Endpoint | Descripcion |
| --- | --- | --- |
| `GET` | `/` | Estado general del backend |
| `POST` | `/detections/detect` | Detecta placas desde una imagen |
| `GET` | `/detections/` | Lista detecciones con filtros |
| `GET` | `/vehicles/` | Lista vehiculos autorizados |
| `POST` | `/vehicles/` | Registra un vehiculo |
| `DELETE` | `/vehicles/{plate}` | Elimina un vehiculo por placa |
| `GET` | `/vehicles/check/{plate}` | Consulta si una placa esta autorizada |
| `GET` | `/alerts/` | Lista alertas |
| `PATCH` | `/alerts/{alert_id}/resolve` | Marca una alerta como resuelta |
| `GET` | `/alerts/count` | Cuenta alertas sin resolver |
| `GET` | `/cameras/` | Lista camaras |
| `POST` | `/cameras/` | Registra camaras |
| `GET` | `/stats/` | Estadisticas basicas |
| `GET` | `/dashboard/` | Resumen para dashboard |
| `POST` | `/simulate/` | Simula una deteccion |
| `POST` | `/api/auth/login` | Login del backend Python |

### Backend Node.js / Express `http://localhost:5000`

| Metodo | Endpoint | Descripcion |
| --- | --- | --- |
| `POST` | `/auth/login` | Login del dashboard |
| `GET` | `/auth/me` | Usuario autenticado |
| `POST` | `/auth/logout` | Cierre de sesion |
| `GET` | `/dashboard/stats` | Indicadores principales |
| `GET` | `/dashboard/recent-detections` | Ultimas detecciones |
| `GET` | `/dashboard/recent-alerts` | Ultimas alertas |
| `GET` | `/api/estadisticas` | Datos de graficas y heatmap |
| `GET` | `/api/audiencias` | Clasificacion de placas por recurrencia |
| `GET` | `/api/camera-intel/:cameraId` | Inteligencia por camara |
| `GET` | `/api/vehicle-profile/:cameraId` | Perfil vehicular por zona |
| `GET` | `/detections` | Detecciones para el dashboard |
| `GET` | `/alertas` | Alertas para el dashboard |
| `PATCH` | `/alertas/:id/resolve` | Resolver alerta |
| `GET` | `/vehicles` | Listar vehiculos |
| `POST` | `/vehicles` | Crear vehiculo |
| `PUT` | `/vehicles/:id` | Actualizar vehiculo |
| `DELETE` | `/vehicles/:id` | Eliminar vehiculo |
| `GET` | `/cameras` | Listar camaras |
| `POST` | `/cameras` | Crear camara |
| `PUT` | `/cameras/:id` | Actualizar camara |
| `DELETE` | `/cameras/:id` | Eliminar camara |
| `GET` | `/simulations` | Listar simulaciones |
| `POST` | `/simulations` | Crear simulacion |
| `GET` | `/users` | Listar usuarios |
| `POST` | `/users` | Crear usuario |
| `PUT` | `/users/:id` | Actualizar usuario |
| `DELETE` | `/users/:id` | Eliminar usuario |

## Paginas Del Dashboard

| Ruta | Funcion |
| --- | --- |
| `/login` | Inicio de sesion |
| `/dashboard` | Resumen general del sistema |
| `/estadisticas` | Graficas de trafico, confianza OCR, heatmap y categorias |
| `/audiencias` | Perfilamiento de placas por recurrencia y valor estimado |
| `/detecciones` | Historial y filtros de detecciones |
| `/alertas` | Alertas de placas no autorizadas |
| `/mapa` | Visualizacion geografica de camaras |
| `/vehiculos` | Gestion de vehiculos autorizados |
| `/camaras` | Gestion de camaras |
| `/usuarios` | Administracion de usuarios |

## Modelo De Base De Datos

### `users`

Usuarios del sistema.

- `id`
- `username`
- `email`
- `password_hash`
- `role`
- `status`
- `created_at`

Roles usados:

- `administrador`: acceso completo.
- `operador`: gestion operativa de vehiculos y camaras.
- `visualizador`: lectura de dashboard, alertas, estadisticas y mapa.

### `cameras`

Camaras registradas.

- `id`
- `camera_code`
- `name`
- `location`
- `status`
- `active`
- `last_connection`
- `created_at`
- `latitud`
- `longitud`

### `vehicles`

Vehiculos autorizados.

- `id`
- `plate`
- `owner`
- `vehicle_type`
- `observations`
- `registered_by`
- `created_at`
- `updated_at`
- `modelo`

### `plates`

Detecciones de placas.

- `id`
- `plate_text`
- `camera_id`
- `vehicle_id`
- `yolo_confidence`
- `ocr_confidence`
- `authorized`
- `image_url`
- `vehicle_type`
- `detection_timestamp`
- `inserted_at`
- `modelo`
- `precio_estimado`

### `alertas`

Alertas creadas cuando una placa no esta autorizada.

- `id`
- `plate_id`
- `camera_id`
- `plate_text`
- `estado_envio`
- `resolved`
- `fecha`
- `inserted_at`

### `simulations`

Registros generados por el simulador.

- `id`
- `camera_code`
- `city`
- `plate_text`
- `vehicle_type`
- `authorized`
- `simulation_timestamp`
- `inserted_at`

## Simulador

El proyecto incluye un simulador en la raiz (`simulador.py`) y endpoints de simulacion en el servidor Express. Sirve para probar el dashboard sin depender siempre de una camara fisica.

Ejecutar desde la raiz, con el backend activo:

```bash
python simulador.py
```

El simulador genera placas, ciudades, tipos de vehiculo y camaras aleatorias.

## Notificaciones Por WhatsApp

Las alertas usan CallMeBot. Para activar un numero:

1. Guardar el contacto de CallMeBot: `+34 644 65 21 68`.
2. Enviar por WhatsApp: `I allow callmebot to send me messages`.
3. Recibir la API key.
4. Configurar en `backend/.env`:

```env
WHATSAPP_NUMBER_1=57XXXXXXXXXX
CALLMEBOT_APIKEY_1=apikey_recibida
```

Se pueden configurar dos destinatarios con `WHATSAPP_NUMBER_2` y `CALLMEBOT_APIKEY_2`.

## Entrenamiento YOLO

El modelo principal del proyecto esta en:

```text
backend/runs/detect/train-5/weights/best.pt
```

Tambien se conservan archivos de entrenamiento como:

- `results.csv`
- `results.png`
- `confusion_matrix.png`
- `confusion_matrix_normalized.png`
- `BoxP_curve.png`
- `BoxR_curve.png`
- `BoxF1_curve.png`
- `BoxPR_curve.png`
- `train_batch*.jpg`
- `val_batch*_labels.jpg`
- `val_batch*_pred.jpg`

Estos archivos sirven como evidencia del entrenamiento y validacion del modelo.

## Uso De Inteligencia Artificial

El proyecto uso IA de dos formas: como parte funcional del sistema y como apoyo durante el desarrollo.

### IA Dentro Del Sistema

| Herramienta | Uso |
| --- | --- |
| YOLOv8 | Detecta la region de la placa en la imagen |
| PaddleOCR | Lee los caracteres de la placa detectada |
| Logica de clasificacion | Normaliza placas, estima datos de vehiculo y clasifica recurrencia |

### IA Como Apoyo De Desarrollo

| Herramienta | Uso en el proyecto |
| --- | --- |
| Claude | Apoyo en arquitectura, schema, endpoints, estadisticas y audiencias |
| OpenAI Codex | Correccion de bugs, documentacion, integracion y revision de codigo |
| Stitch AI | Propuesta inicial de componentes y layout |
| Figma | Refinamiento visual del dashboard |
| Replit | Prototipado inicial del frontend |

Todo el codigo fue revisado por el equipo y cada integrante debe poder explicar la parte que desarrollo durante la sustentacion.

## Pruebas Y Verificacion

Pruebas disponibles:

```bash
cd backend
python test_whatsapp.py
python test_deteccion_alerta.py
```

Verificaciones recomendadas:

- Abrir `http://localhost:8000/docs` y probar `GET /`.
- Iniciar sesion en `http://localhost:5000`.
- Registrar un vehiculo autorizado.
- Ejecutar una simulacion.
- Subir una imagen a `POST /detections/detect`.
- Confirmar que la deteccion aparezca en `plates`.
- Confirmar que una placa no registrada cree alerta en `alertas`.
- Confirmar que WhatsApp reciba la alerta si CallMeBot esta configurado.

## Estado Actual

Implementado:

- Backend Python con FastAPI.
- Modelo YOLO y OCR con PaddleOCR.
- Persistencia en Supabase.
- Storage de imagenes.
- Backend Express para dashboard.
- Frontend React con rutas protegidas.
- CRUD de vehiculos, camaras y usuarios.
- Detecciones, alertas, estadisticas, audiencias y mapa.
- Notificaciones WhatsApp con CallMeBot.
- Script de arranque automatico para Windows.

Pendiente o por revisar:

- Activar la API key de CallMeBot para el segundo numero.
- Validar que todos los roles requeridos existan en la tabla `users`.
- Rotar cualquier llave real que haya sido compartida fuera de archivos `.env`.
- Verificar la rubrica final del profesor contra este README.
- Asegurar que cada integrante tenga los commits requeridos en GitHub.

## Comandos Utiles

Backend:

```bash
venv\Scripts\activate
cd backend
uvicorn api:app --reload --host localhost --port 8000
```

Frontend:

```bash
cd frontend-dashboard
npm run dev
```

Revision TypeScript:

```bash
cd frontend-dashboard
npm run check
```

Build:

```bash
cd frontend-dashboard
npm run build
```

## Informacion Academica

- **Materia:** Programacion Avanzada
- **Universidad:** Universidad de La Guajira
- **Periodo:** 2026-I
- **Docente:** Eduardo Sierra
- **Proyecto:** Sistema Inteligente de Reconocimiento de Placas - LPR Smart City

