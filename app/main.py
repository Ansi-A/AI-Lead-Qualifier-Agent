from fastapi import FastAPI
from .database.db import engine, Base
from .routes.lead_routes import router as lead_router
from .routes import auth, users
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logger
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()
setup_logger()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])
# Include routers
app.include_router(lead_router)
app.include_router(auth.router)
app.include_router(users.router)

# Create tables ( we might use Alembic for migrations in future so this is just for now a testing   pint)
Base.metadata.create_all(bind=engine)




