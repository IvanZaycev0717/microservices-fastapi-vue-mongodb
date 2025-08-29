from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routes import about
import os
from services.logger import get_logger

logger = get_logger("content_service_main")

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "content_db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    yield
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Content Service",
    description="Microservice for content management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.url}"
        )
        return response
    except Exception as e:
        logger.error(f"Error processing request {request.method} {request.url}: {e}")
        raise


app.include_router(about.router)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Content Service is running"}


@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")
    try:
        logger.info("Health check: MongoDB connection OK")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
