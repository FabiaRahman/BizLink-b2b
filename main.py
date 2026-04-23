# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import orders, refunds, error_logs, manual_reviews  # ← ADD manual_reviews

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")
    print("📦 Tables: orders, refunds, error_logs, manual_reviews")
    yield

app = FastAPI(
    title="BizLink B2B Workflow Automation",
    description="Backend API for BizLink platform - CSE 314 Group 3",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(orders.router)
app.include_router(refunds.router)
app.include_router(error_logs.router)
app.include_router(manual_reviews.router)  # ← ADD THIS

@app.get("/", operation_id="root_health_check")
def root():
    return {
        "message": "BizLink backend is running",
        "endpoints": {
            "orders": "/orders",
            "refunds": "/refunds", 
            "error_logs": "/error-logs",
            "manual_reviews": "/manual-reviews",
            "docs": "/docs"
        }
    }