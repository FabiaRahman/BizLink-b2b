# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import orders, refunds

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create all database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")
    yield

app = FastAPI(
    title="BizLink B2B Workflow Automation",
    description="Backend API for BizLink platform - CSE 314 Group 3",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(orders.router)
app.include_router(refunds.router)

@app.get("/", operation_id="root_health_check")
def root():
    return {"message": "BizLink backend is running"}