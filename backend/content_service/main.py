from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import about

app = FastAPI(
    title="Content Service",
    description="Microservice for content management",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(about.router)


@app.get("/")
async def root():
    return {"message": "Content Service is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8001)
