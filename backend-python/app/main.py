import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config.database import engine, Base
from app.config.logger import logger
from app.config.settings import settings
from app.routers import auth, tasks, users

# Create DB tables on startup (equivalent to prisma migrate deploy)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready")
    yield
    logger.info("Shutting down")


# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="Task Manager API",
    description="REST API with Authentication & Role-Based Access Control",
    version="1.0.0",
    docs_url="/api/docs",       # Swagger UI  (same path as Node.js version)
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://crud-app-seven.vercel.app",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logger middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} → {response.status_code}")
        return response
    except Exception as exc:
        logger.error(f"{request.method} {request.url.path} — {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Internal server error"},
        )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"{request.method} {request.url.path} — {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"},
    )


# Health check
@app.get("/health", tags=["Health"])
def health():
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# Routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)

if __name__ == "__main__":
    import uvicorn
    os.makedirs("logs", exist_ok=True)
    logger.info(f"Server running on http://localhost:{settings.PORT}")
    logger.info(f"API Docs at http://localhost:{settings.PORT}/api/docs")
    # Run from backend-python/ with: poetry run uvicorn app.main:app --reload
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True, app_dir="..")
