from fastapi import FastAPI
from app.database import engine, Base
from app.routes import orders

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BizLink B2B Workflow Automation",
    version="1.0.0",
    description="Backend API for BizLink platform - CSE 314 Group 3"
)

# Include routers
app.include_router(orders.router)

@app.get("/")
def root():
    return {"message": "BizLink backend is running"}