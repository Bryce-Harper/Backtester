from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health

app = FastAPI(
    title="Momentum Backtester API",
    description="Backend API for the momentum-backtester app.",
    version="0.1.0",
)

# Allow the Vite dev server to call the API directly during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
