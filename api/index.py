from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback
import sys
import os

from app.api.endpoints import router as api_router
from app.db.base import engine, Base

# Resilient table creation
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False

db_initialized = init_db()

app = FastAPI(
    title="Nexus API",
    description="The brain of the N\u00fcmtema AI FOUNDRY mission engine.",
    version="1.0.0"
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "traceback": traceback.format_exc(),
            "cwd": os.getcwd(),
            "path": sys.path
        },
    )

app.include_router(api_router, prefix="/v1")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "Nexus API",
        "status": "online",
        "db_status": "connected" if db_initialized else "disconnected/error",
        "version": "1.0.0",
        "org": "N\u00fcmtema AI FOUNDRY"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
