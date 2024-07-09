from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from routes import app_routes
from logger import setup_logging
from firebase_service import initialize_firebase
from exceptions import CustomException, handle_custom_exception

logger = setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(title="AOI WhatsApp Bot Service",
                  description="A service to handle WhatsApp messages using Twilio, Firebase, and OpenAI for the AI Objectives Institute.",
                  version="1.0.0")

    # Initialize Firebase
    initialize_firebase()

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Include routes
    app.include_router(app_routes)

    # Event handlers
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up the AOI WhatsApp Bot Service...")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down the AOI WhatsApp Bot Service...")

    # Exception handlers
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": f"HTTP error occurred: {exc.detail}"}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=400,
            content={"message": "Validation error", "errors": exc.errors()}
        )

    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return handle_custom_exception(request, exc)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
