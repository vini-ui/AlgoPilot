from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, apps, strategies, orders, settings
from app.models.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AlgoPilot API",
    description="Trading Automation Platform API",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5180", "http://127.0.0.1:5180"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(apps.router, prefix="/api/apps", tags=["apps"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])


@app.get("/")
async def root():
    return {"message": "AlgoPilot API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

