from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.endpoints import content, auth, comments
from logger import get_logger
from settings import settings
from services.redis_connect_management import redis_manager

logger = get_logger("API Gateway")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager.

    Handles startup and shutdown procedures including Redis connections.
    """
    logger.info(
        f"{settings.API_GATEWAY_NAME} starting on {settings.API_GATEWAY_HOST}:{settings.API_GATEWAY_PORT}"
    )
    await redis_manager.connect()
    app.state.redis_manager = redis_manager
    yield
    await redis_manager.disconnect()
    logger.info(f"{settings.API_GATEWAY_NAME} shutting down")


app = FastAPI(
    title=settings.API_GATEWAY_NAME, version="1.0.0", lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(content.router, tags=["content"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(comments.router, tags=["comments"])
app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.API_GATEWAY_NAME}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.API_GATEWAY_HOST,
        port=settings.API_GATEWAY_PORT,
    )
