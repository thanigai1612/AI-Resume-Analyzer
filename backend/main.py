from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.database import engine, Base, SessionLocal
from app.models.models import User
from app.core.security import get_password_hash

# Import routers
from app.api.auth import router as auth_router
from app.api.resumes import router as resumes_router
from app.api.jobs import router as jobs_router
from app.api.analysis import router as analysis_router
from app.api.ai_assist import router as ai_assist_router
from app.api.admin import router as admin_router
from app.api.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    Base.metadata.create_all(bind=engine)

def seed_admin():
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        db = SessionLocal()
        try:
            admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
            if not admin:
                logger.info(f"Seeding default admin user: {settings.ADMIN_EMAIL}")
                hashed_pwd = get_password_hash(settings.ADMIN_PASSWORD)
                new_admin = User(
                    email=settings.ADMIN_EMAIL,
                    hashed_password=hashed_pwd,
                    full_name="System Admin",
                    is_admin=True
                )
                db.add(new_admin)
                db.commit()
        except Exception as e:
            logger.error(f"Error seeding admin user: {e}")
        finally:
            db.close()

# Initialize tables
create_tables()

app = FastAPI(
    title="AI Resume Analyzer API",
    description="Backend for the AI Resume Analyzer Application.",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vite default frontend port
    "http://localhost:3000",
    "*"  # Allow all for development. Restrict in production.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
def startup_event():
    seed_admin()

# Register Routers
app.include_router(auth_router)
app.include_router(resumes_router)
app.include_router(jobs_router)
app.include_router(analysis_router)
app.include_router(ai_assist_router)
app.include_router(admin_router)
app.include_router(health_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
