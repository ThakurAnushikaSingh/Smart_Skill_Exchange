from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.api.routes.auth import router as auth_router
from app.api.routes.profile import router as profile_router
from app.api.routes.requests import router as requests_router
from app.api.routes.skills import router as skills_router
from app.core.config import get_settings
from app.services.base import ServiceError

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.exception_handler(ServiceError)
async def service_error_handler(_: Request, exc: ServiceError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(skills_router)
app.include_router(requests_router)
