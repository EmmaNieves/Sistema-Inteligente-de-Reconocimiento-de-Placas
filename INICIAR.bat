@echo off
chcp 65001 >nul
title PlacaControl — Iniciando sistema...
color 0A

echo.
echo  ██████╗ ██╗      █████╗  ██████╗ █████╗      
echo  ██╔══██╗██║     ██╔══██╗██╔════╝██╔══██╗     
echo  ██████╔╝██║     ███████║██║     ███████║     
echo  ██╔═══╝ ██║     ██╔══██║██║     ██╔══██║     
echo  ██║     ███████╗██║  ██║╚██████╗██║  ██║     
echo  ╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝     
echo  Sistema Inteligente de Reconocimiento de Placas
echo  Universidad de La Guajira — 2026-I
echo.
echo ============================================================
echo.

:: ── Verificar que estamos en la carpeta correcta ─────────────
if not exist "backend\api.py" (
    echo [ERROR] Ejecuta este .bat desde la raiz del proyecto.
    echo         La carpeta debe contener las carpetas backend\ y frontend-dashboard\
    pause
    exit /b 1
)

:: ── PASO 1: Verificar Python ─────────────────────────────────
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instala Python 3.10+ desde https://python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo        %%v encontrado OK
echo.

:: ── PASO 2: Verificar Node.js ────────────────────────────────
echo [2/6] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no encontrado. Instala Node.js 18+ desde https://nodejs.org
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version') do echo        Node %%v encontrado OK
echo.

:: ── PASO 3: Verificar .env del backend ──────────────────────
echo [3/6] Verificando archivos .env...
if not exist "backend\.env" (
    echo [AVISO] No se encontro backend\.env
    echo         Creando archivo de ejemplo...
    (
        echo SUPABASE_URL=https://ecwomhimxcypilnuatdn.supabase.co
        echo SUPABASE_KEY=TU_SUPABASE_ANON_KEY
        echo SUPABASE_SERVICE_KEY=TU_SUPABASE_SERVICE_KEY
        echo SUPABASE_STORAGE_BUCKET=plate-images
        echo JWT_SECRET=mi_clave_super_secreta_2024
        echo WHATSAPP_NUMBER_1=573243333381
        echo CALLMEBOT_APIKEY_1=TU_APIKEY_CALLMEBOT
        echo WHATSAPP_NUMBER_2=573332487255
        echo CALLMEBOT_APIKEY_2=
    ) > backend\.env
    echo         Archivo creado. EDITA backend\.env con tus claves reales antes de continuar.
    echo.
    pause
)
if not exist "frontend-dashboard\.env" (
    echo [AVISO] No se encontro frontend-dashboard\.env
    echo         Creando archivo de ejemplo...
    (
        echo SUPABASE_URL=https://ecwomhimxcypilnuatdn.supabase.co
        echo SUPABASE_SERVICE_KEY=TU_SUPABASE_SERVICE_KEY
        echo JWT_SECRET=mi_clave_super_secreta_2024
    ) > frontend-dashboard\.env
    echo         Archivo creado. EDITA frontend-dashboard\.env con tus claves reales.
    echo.
    pause
)
echo        .env encontrados OK
echo.

:: ── PASO 4: Instalar dependencias Python ─────────────────────
echo [4/6] Instalando dependencias Python (puede tardar la primera vez)...
cd backend
if exist "..\venv\Scripts\activate.bat" (
    echo        Usando entorno virtual existente...
    call ..\venv\Scripts\activate.bat
) else (
    echo        Creando entorno virtual...
    python -m venv ..\venv
    call ..\venv\Scripts\activate.bat
)
pip install -r ..\requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias Python.
    echo         Intenta correr manualmente: pip install -r requirements.txt
    pause
    exit /b 1
)
echo        Dependencias Python OK
cd ..
echo.

:: ── PASO 5: Instalar dependencias Node ──────────────────────
echo [5/6] Instalando dependencias Node.js...
cd frontend-dashboard
if not exist "node_modules" (
    echo        Primera vez — instalando paquetes npm (puede tardar)...
    call npm install --silent
    if errorlevel 1 (
        echo [ERROR] Fallo npm install. Intenta manualmente: cd frontend-dashboard ^&^& npm install
        pause
        exit /b 1
    )
) else (
    echo        node_modules ya existe, omitiendo instalacion
)
cd ..
echo        Dependencias Node OK
echo.

:: ── PASO 6: Matar proceso en puerto 5000 si existe ──────────
echo [6/6] Liberando puertos...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
)
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":5000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
)
echo        Puertos 5000 y 8000 liberados
echo.

:: ── ARRANCAR BACKEND ─────────────────────────────────────────
echo ============================================================
echo  Iniciando Backend (FastAPI - Puerto 8000)...
echo ============================================================
start "PlacaControl - BACKEND" cmd /k "cd /d %~dp0backend && call %~dp0venv\Scripts\activate.bat && uvicorn api:app --reload --port 8000 --host localhost"

timeout /t 4 /nobreak >nul

:: ── ARRANCAR FRONTEND ────────────────────────────────────────
echo  Iniciando Frontend (Express+React - Puerto 5000)...
echo ============================================================
start "PlacaControl - FRONTEND" cmd /k "cd /d %~dp0frontend-dashboard && npm run dev"

timeout /t 5 /nobreak >nul

:: ── ABRIR NAVEGADOR ──────────────────────────────────────────
echo.
echo ============================================================
echo  Abriendo http://localhost:5000 en el navegador...
echo ============================================================
start "" "http://localhost:5000"

echo.
echo  Sistema iniciado correctamente.
echo  Backend:  http://localhost:8000/docs  (Swagger)
echo  Frontend: http://localhost:5000
echo.
echo  Cierra las ventanas negras para apagar el sistema.
echo ============================================================
pause
