try:
    import sys
    import os
    # Force inclusion of the current directory in sys.path
    # This ensures 'app' can be found regardless of how Vercel starts the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    print(f"DEBUG: sys.path is {sys.path}")

    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import traceback

    from app.api.endpoints import router as api_router
    from app.db.base import engine, Base
    
    # Resilient table creation
    def init_db():
        try:
            Base.metadata.create_all(bind=engine)
            return True
        except Exception as e:
            print(f"DATABASE INIT ERROR: {e}")
            return False

    db_initialized = init_db()

    app = FastAPI(
        title="Nexus API",
        description="The brain of the Nümtéma AI FOUNDRY mission engine.",
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
                "path": sys.path,
                "initialized": db_initialized
            },
        )

    app.include_router(api_router, prefix="/v1")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {
            "name": "Nexus API",
            "status": "online",
            "db": "connected" if db_initialized else "error",
            "msg": "Nexus System Ready. All systems nominal."
        }

except Exception as boot_error:
    # If anything crashes during boot, we try to create a minimal app to report it
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/{path:path}")
    async def catch_all(path: str):
        import traceback
        return {
            "error": "CRITICAL_BOOT_FAILURE",
            "detail": str(boot_error),
            "traceback": traceback.format_exc()
        }
