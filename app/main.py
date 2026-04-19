from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import orders

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create all database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")
    yield
    # Shutdown: (optional cleanup here if needed)

app = FastAPI(
    title="BizLink B2B Workflow Automation",
    description="Backend API for BizLink platform - CSE 314 Group 3",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(orders.router)

@app.get("/")
def root():
    return {"message": "BizLink backend is running"}