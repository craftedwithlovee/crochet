"""
Crafted with Love — FastAPI Backend
Run: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .database import engine, Base
from .models import Admin
from .auth import get_current_admin
from .routes import products, categories, admin
from .limiter import limiter

# Resolve project root (one level up from backend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    # Create uploads directory
    uploads_dir = PROJECT_ROOT / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    yield

app = FastAPI(
    title="Crafted with Love API",
    description="Backend API for the Crochet Studio e-commerce store",
    version="1.0.0",
    lifespan=lifespan,
)

# Connect rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow all for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression — reduces payload size for faster loading
app.add_middleware(GZipMiddleware, minimum_size=500)


# Cache and Security headers for API responses
@app.middleware("http")
async def add_security_and_cache_headers(request: Request, call_next):
    # Process request
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Basic CSP - limit script execution
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https:; script-src 'self' 'unsafe-inline' https:; frame-ancestors 'none'"

    path = request.url.path
    # Cache images and static assets aggressively
    if path.startswith("/images/") or path.startswith("/uploads/"):
        response.headers["Cache-Control"] = "public, max-age=86400"  # 24 hours
    # Cache API GET responses for a short time
    elif path.startswith("/api/") and request.method == "GET":
        response.headers["Cache-Control"] = "public, max-age=5"  # 5 seconds
    
    return response

# Include API routers
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(admin.router)


# ── Image Upload Endpoint ────────────────────────────────────────────────────

@app.post("/api/upload", tags=["Upload"])
async def upload_image(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin),
):
    """Upload a product image. Returns the relative path for use in product records."""
    uploads_dir = PROJECT_ROOT / "uploads"
    uploads_dir.mkdir(exist_ok=True)

    # Sanitize filename
    safe_name = file.filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
    file_path = uploads_dir / safe_name

    # Avoid overwriting
    counter = 1
    stem = file_path.stem
    suffix = file_path.suffix
    while file_path.exists():
        file_path = uploads_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    relative_path = f"uploads/{file_path.name}"
    return {"path": relative_path, "filename": file_path.name}


# ── Static Files ─────────────────────────────────────────────────────────────

# Serve uploaded images
app.mount("/uploads", StaticFiles(directory=str(PROJECT_ROOT / "uploads")), name="uploads")

# Serve existing product images
app.mount("/images", StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "images")), name="images")

# Serve admin panel
app.mount("/admin", StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "admin"), html=True), name="admin")


# ── Storefront ───────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def serve_storefront():
    return FileResponse(str(PROJECT_ROOT / "frontend" / "index.html"))
