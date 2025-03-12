from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import plates, bids, auth
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_url=f"/{settings.APP_VERSION}/openapi.json",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include routers
app.include_router(auth.auth_router, prefix=settings.API_PREFIX)
app.include_router(plates.router, prefix=settings.API_PREFIX)
app.include_router(bids.router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    """
    Root endpoint that returns basic API information.
    """
    return {
        "message": "Welcome to the License Plate Bidding System API",
        "documentation": f"/docs",
        "api_version": settings.API_PREFIX
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)