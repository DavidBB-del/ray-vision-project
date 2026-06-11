from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.reconstruction import router as reconstruction_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered medical image reconstruction service for Ray-Vision.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Ray-Vision-Task", "X-Ray-Vision-Iterations"],
)


@app.get(f"{settings.api_prefix}/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


app.include_router(reconstruction_router, prefix=settings.api_prefix)
