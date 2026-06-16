from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes.detections import router as detections_router
from routes.vehicles import router as vehicles_router
from routes.alerts import router as alerts_router
from routes.cameras import router as cameras_router
from routes.stats import router as stats_router
from routes.simulador import router as simulator_router
from routes.dashboard import router as dashboard_router
from routes.routes_auth import router as auth_router

app = FastAPI(
    title="Sistema de Reconocimiento de Placas",
    version="2.0.0"
)

# ── CORS — permite peticiones desde el frontend Next.js ──────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(detections_router)
app.include_router(vehicles_router)
app.include_router(alerts_router)
app.include_router(cameras_router)
app.include_router(stats_router)
app.include_router(simulator_router)
app.include_router(dashboard_router)
app.include_router(auth_router)




@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"status": "ok", "version": "2.0.0", "mensaje": "Sistema de placas activo"}


# ── Backward-compat — endpoints anteriores siguen funcionando ─────────────────
from database import get_all_plates

@app.get("/placas")
def listar_placas():
    return {"placas": get_all_plates()}
