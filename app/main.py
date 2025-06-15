from fastapi import FastAPI
from app.core.config import get_settings
from app.api.routes import price

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(price.router)


@app.get("/")
async def root():
    return {"message": "Welcome to PriceFetch API"}
