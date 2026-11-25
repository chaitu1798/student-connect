import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.limiter import limiter
from app.database import Base, engine, SessionLocal
from app.routers import (
    auth,
    public,
    admin_students,
    internships,
    imports,
    analytics,
    documents,
    reports,
    admin,
    pdf_extract,
)
from app.models.user import User
from app.models.organization import Branch, College
from app.utils.security import hash_password

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Student Information & Internship Management System API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Attach SlowAPI Limiter state and rate limit exceeded exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security Response Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    is_prod = settings.ENVIRONMENT == "production"

    if is_prod:
        script_src = "'self'"
        connect_src = "'self'"
    else:
        script_src = "'self' 'unsafe-inline' 'unsafe-eval'"
        connect_src = "'self' http://localhost:* http://127.0.0.1:* ws://localhost:* ws://127.0.0.1:*"

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Modern OWASP standard: disable legacy buggy XSS auditor in favor of strict CSP
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = (
        f"default-src 'self'; "
        f"script-src {script_src}; "
        f"style-src 'self' 'unsafe-inline'; "
        f"img-src 'self' data: blob:; "
        f"font-src 'self' data:; "
        f"connect-src {connect_src}; "
        f"frame-ancestors 'none';"
    )
    if is_prod or request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# CORS Middleware (Explicit allowlist enforced; wildcards rejected when credentials allowed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API v1 endpoints
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(public.router, prefix=settings.API_V1_STR)
app.include_router(admin_students.router, prefix=settings.API_V1_STR)
app.include_router(internships.router, prefix=settings.API_V1_STR)
app.include_router(imports.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(pdf_extract.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        is_production = settings.ENVIRONMENT == "production"

        if is_production:
            # In production, NEVER auto-seed default credentials
            super_admin_count = db.query(User).filter(User.role == "SUPER_ADMIN").count()
            if super_admin_count == 0:
                logging.getLogger("uvicorn.error").warning(
                    "[SECURITY ALERT] No SUPER_ADMIN user found in production database. "
                    "Run 'python -m app.cli bootstrap-admin' to create the initial administrator securely."
                )
        else:
            # Default Super Admin user for development/testing
            admin_user = db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USERNAME).first()
            if not admin_user:
                admin_user = User(
                    username=settings.DEFAULT_ADMIN_USERNAME,
                    email=settings.DEFAULT_ADMIN_EMAIL,
                    full_name="System Administrator",
                    role="SUPER_ADMIN",
                    hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                    must_change_password=False,
                    mfa_enabled=False,
                )
                db.add(admin_user)

            # Default Client user for development/testing
            client_user = db.query(User).filter(User.username == "client").first()
            if not client_user:
                client_user = User(
                    username="client",
                    email="client@institution.edu",
                    full_name="Placement & Records Officer",
                    role="CLIENT",
                    hashed_password=hash_password("Client123!"),
                    must_change_password=False,
                    mfa_enabled=False,
                )
                db.add(client_user)

        # Branches
        branch_seeds = [
            ("CSE", "Computer Science & Engineering"),
            ("ECE", "Electronics & Communication Engineering"),
            ("IT", "Information Technology"),
            ("EEE", "Electrical & Electronics Engineering"),
            ("MECH", "Mechanical Engineering"),
            ("CIVIL", "Civil Engineering"),
            ("AI_DS", "Artificial Intelligence & Data Science"),
        ]
        for code, name in branch_seeds:
            if not db.query(Branch).filter(Branch.code == code).first():
                db.add(Branch(code=code, name=name))

        # College
        if not db.query(College).filter(College.code == "UCE").first():
            db.add(College(code="UCE", name="Vignan's Institute Of Information Technology"))

        db.commit()
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "normalized-uuid",
    }
