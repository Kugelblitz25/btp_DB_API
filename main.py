"""Main application file for the People Tracking API.

This file initializes the FastAPI application, includes the necessary routers,
and defines startup events and a root endpoint.
"""
import uvicorn
from fastapi import FastAPI

from database import create_db_and_tables
from routers.event import router as event_router

# Import routers
from routers.person import router as person_router

# FastAPI application instance
app: FastAPI = FastAPI(title="People Tracking API")

# Include routers for different API modules
app.include_router(person_router)
app.include_router(event_router)


@app.on_event("startup")
async def on_startup() -> None:
    """
    Handles application startup events.

    This function is executed when the application starts up. It calls
    the `create_db_and_tables` function to ensure that all necessary
    database tables are created.
    """
    await create_db_and_tables()


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint for the API.

    Returns:
        dict[str, str]: A welcome message.
    """
    return {"message": "Welcome to the People Tracking API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
