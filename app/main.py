from fastapi import FastAPI
from .database.db import engine, Base
from .routes.lead_routes import router as lead_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Include routers
app.include_router(lead_router)

# Create tables
Base.metadata.create_all(bind=engine)
