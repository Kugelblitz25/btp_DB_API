from fastapi import FastAPI
import uvicorn
from database import create_db_and_tables

# Import routers
from routers.person import router as person_router
from routers.event import router as event_router

app = FastAPI(title="People Tracking API")

# Include routers
app.include_router(person_router)
app.include_router(event_router)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to the People Tracking API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)