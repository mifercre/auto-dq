from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.api import api_router_admin
from core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f'{settings.API_PREFIX_ADMIN}/openapi.json'
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
        expose_headers=['*']
    )

# Admin routes
app.include_router(
    api_router_admin,
    prefix=settings.API_PREFIX_ADMIN,
    dependencies=[],
    responses={404: {'description': 'Not found'}}
)

# Start scheduler (this will remove and restart all jobs)
from scheduler import scheduler
scheduler.app_init_start()
