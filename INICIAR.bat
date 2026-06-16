@echo off
chcp 65001 >nul
title PlacaControl - Iniciando...
color 0A

echo.
echo  =========================================
echo   PlacaControl - Sistema de Placas
echo   Universidad de La Guajira 2026-I
echo  =========================================
echo.

:: ── Ubicarse en la carpeta del .bat sin importar desde donde se ejecute ──
cd /d "%~dp0"

:: ══════════════════════════════════════════════════════════
:: PASO 1 — Crear backend\.env con todas las keys reales
:: ══════════════════════════════════════════════════════════
echo [1/5] Configurando variables de entorno del backend...
(
echo SUPABASE_URL=https://ecwomhimxcypilnuatdn.supabase.co
echo SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjd29taGlteGN5cGlsbnVhdGRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcwNzM0MTAsImV4cCI6MjA5MjY0OTQxMH0.uqHcrfBjNTNXaRNbD-BlO6dv6HjmNXnCd9buA9Rn-1w
echo SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjd29taGlteGN5cGlsbnVhdGRuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzA3MzQxMCwiZXhwIjoyMDkyNjQ5NDEwfQ.ms4i4gRlYIdJOnxIaUkLxDspmPIbZmg1Y5iXcUXFI3I
echo SUPABASE_STORAGE_BUCKET=plate-images
echo JWT_SECRET=/uE/ZUYTe3w5j0hE9+e5yUMWWpzgAEpVS36k/unYR5Yzau0QR/OPosTWCtMn9LNphUTXvrFVAtg/QEnu9J5bpg==
echo WHATSAPP_NUMBER_1=573243333381
echo CALLMEBOT_APIKEY_1=2995336
echo WHATSAPP_NUMBER_2=573332487255
echo CALLMEBOT_APIKEY_2=
echo WHATSAPP_TOKEN=sin_configurar
echo PHONE_NUMBER_ID=sin_configurar
) > backend\.env
echo        backend\.env creado OK

:: ══════════════════════════════════════════════════════════
:: PASO 2 — Crear frontend-dashboard\.env con todas las keys
:: ══════════════════════════════════════════════════════════
echo [2/5] Configurando variables de entorno del frontend...
(
echo SUPABASE_URL=https://ecwomhimxcypilnuatdn.supabase.co
echo SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjd29taGlteGN5cGlsbnVhdGRuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzA3MzQxMCwiZXhwIjoyMDkyNjQ5NDEwfQ.ms4i4gRlYIdJOnxIaUkLxDspmPIbZmg1Y5iXcUXFI3I
echo JWT_SECRET=/uE/ZUYTe3w5j0hE9+e5yUMWWpzgAEpVS36k/unYR5Yzau0QR/OPosTWCtMn9LNphUTXvrFVAtg/QEnu9J5bpg==
) > frontend-dashboard\.env
echo        frontend-dashboard\.env creado OK
echo.

:: ══════════════════════════════════════════════════════════
:: PASO 3 — Instalar dependencias Python
:: ══════════════════════════════════════════════════════════
echo [3/5] Instalando dependencias Python...
if not exist venv (
    echo        Creando entorno virtual...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -q --disable-pip-version-check
echo        Dependencias Python OK
echo.

:: ══════════════════════════════════════════════════════════
:: PASO 4 — Instalar dependencias Node
:: ══════════════════════════════════════════════════════════
echo [4/5] Instalando dependencias Node.js...
if not exist frontend-dashboard\node_modules (
    echo        Primera vez - esto puede tardar unos minutos...
    cd frontend-dashboard
    call npm install --silent
    cd ..
) else (
    echo        node_modules ya existe, omitiendo...
)
echo        Dependencias Node OK
echo.

:: ══════════════════════════════════════════════════════════
:: PASO 5 — Liberar puertos y arrancar servidores
:: ══════════════════════════════════════════════════════════
echo [5/5] Liberando puertos y arrancando servidores...

for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do taskkill /PID %%p /F >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":5000 " ^| findstr "LISTENING"') do taskkill /PID %%p /F >nul 2>&1

:: Arrancar backend en ventana separada
start "BACKEND - PlacaControl" cmd /k "cd /d "%~dp0backend" && call "%~dp0venv\Scripts\activate.bat" && echo Backend iniciando en http://localhost:8000 && uvicorn api:app --reload --port 8000 --host localhost"

:: Esperar 4 segundos a que el backend levante
timeout /t 4 /nobreak >nul

:: Arrancar frontend en ventana separada
start "FRONTEND - PlacaControl" cmd /k "cd /d "%~dp0frontend-dashboard" && echo Frontend iniciando en http://localhost:5000 && npm run dev"

:: Esperar 6 segundos a que el frontend levante
timeout /t 6 /nobreak >nul

:: Abrir el navegador
echo        Abriendo http://localhost:5000 ...
start "" "http://localhost:5000"

echo.
echo  =========================================
echo   Sistema iniciado correctamente
echo   Frontend:  http://localhost:5000
echo   Backend:   http://localhost:8000/docs
echo  =========================================
echo.
echo  Deja abiertas las dos ventanas negras.
echo  Para apagar: cierra las ventanas negras.
echo.
pause
