import os
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.core.registry import MODULE_REGISTRY, get_active_routers
from backend.init_db import init_db
from backend.utils.notifications import (
    get_user_notifications,
    mark_notification_as_read
)

# Initialize FastAPI application
app = FastAPI(
    title="MandiSetu API",
    description="AI-Powered Market-Intelligence and Transaction Platform (SIH26132 - Govt. of Maharashtra)",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lifespan / Startup Hook
@app.on_event("startup")
def on_startup():
    print("[MandiSetu] Initializing database tables...")
    init_db()
    print("[MandiSetu] Database ready.")

# Include module routers dynamically from registry
for router, meta in get_active_routers():
    app.include_router(
        router,
        tags=meta.get("tags", [])
    )
    print(f"[MandiSetu] Mounted router for {meta['id']} ({meta['name']})")

# Mount static frontend directories for each module
base_dir = settings.BASE_DIR
for item in MODULE_REGISTRY:
    module_folder = base_dir / item["folder"] / "frontend"
    if module_folder.exists() and module_folder.is_dir():
        mount_url = f"/modules/{item['static_mount']}"
        app.mount(
            mount_url,
            StaticFiles(directory=str(module_folder), html=True),
            name=f"static_{item['id']}"
        )
        print(f"[MandiSetu] Mounted static assets for {item['id']} at {mount_url}")

# Mount shared frontend assets
frontend_dir = settings.FRONTEND_DIR
if frontend_dir.exists():
    css_dir = frontend_dir / "css"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")

    js_dir = frontend_dir / "js"
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

    i18n_dir = frontend_dir / "i18n"
    if i18n_dir.exists():
        app.mount("/i18n", StaticFiles(directory=str(i18n_dir)), name="i18n")

    assets_dir = frontend_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# Root & Dashboard Routes
@app.get("/", summary="Landing & Login Page")
def serve_index():
    index_file = settings.FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"message": "MandiSetu API is active. Frontend index.html not yet found."})

@app.get("/dashboard", summary="Role-Based Command Center")
def serve_dashboard():
    dash_file = settings.FRONTEND_DIR / "dashboard.html"
    if dash_file.exists():
        return FileResponse(str(dash_file))
    return JSONResponse({"message": "Frontend dashboard.html not yet found."})

# System Health & Info
@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "MandiSetu 2.0",
        "challenge": "SIH26132 (Govt. of Maharashtra)",
        "modules_registered": len(MODULE_REGISTRY),
        "active_modules": [m["name"] for m in MODULE_REGISTRY if m.get("enabled", False)]
    }

# Shared Notifications Endpoints
@app.get("/api/notifications", tags=["Notifications"])
def list_notifications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    notifs = get_user_notifications(db, current_user.id)
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "category": n.category,
            "link": n.link,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None
        }
        for n in notifs
    ]

@app.post("/api/notifications/{notification_id}/read", tags=["Notifications"])
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    success = mark_notification_as_read(db, notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True}
