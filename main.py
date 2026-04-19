
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


from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import orders

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")
    yield


app = FastAPI(
    title="BizLink B2B Workflow Automation",
    description="Backend API for BizLink platform - CSE 314 Group 3",

    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "BizLink backend is running"}

    version="1.0.0",
    lifespan=lifespan


app.include_router(orders.router)

@app.get("/")
def root():
    return {"message": "BizLink backend is running"}

