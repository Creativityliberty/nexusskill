from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router as api_router
from app.db.base import engine, Base

# Create tables on startup (simple approach for Phase 2)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nexus API",
    description="The brain of the N\u00fcmtema AI FOUNDRY mission engine.",
    version="1.0.0"
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
        "version": "1.0.0",
        "org": "N\u00fcmtema AI FOUNDRY"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
