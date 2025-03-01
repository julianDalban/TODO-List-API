from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import CustomHTTPException
from app.core.config import settings
from app.api.routes import api_router
from app.schemas.task import MessageResponse
from app.db.init_db import init_db

app = FastAPI(title=settings.PROJECT_NAME) # Create FastAPI instance

init_db() # initialise database tables

app.include_router(api_router, prefix=settings.API_V1_STR) # Include API Router

@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=MessageResponse(
            message='Error',
            data={
                'detail': exc.detail,
                'error_code': exc.error_code
            },
            status=exc.status_code
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=MessageResponse(
            message='Error',
            data={
                'detail': str(exc),
                'error_code': 'VALIDATION_ERROR'
            },
            status=422
        ).model_dump()
    )

@app.get('/')
def root():
    return {'message': f'Welcome to {settings.PROJECT_NAME}'}