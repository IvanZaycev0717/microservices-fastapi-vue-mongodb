from fastapi import FastAPI
from routes import content
from fastapi.middleware.cors import CORSMiddleware

from settings import PREFIX_URL

app = FastAPI(
    title="API Gateway",
    description="Gateway for microservices architecture",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(content.router, prefix=PREFIX_URL)


@app.get("/")
async def root():
    return {
        "message": "API Gateway is running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
