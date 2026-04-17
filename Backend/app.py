from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db
from routes.auth import router as auth_router
from routes.predict import router as predict_router

app = FastAPI(
    title="LigBind API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(predict_router)

@app.get("/")
def home():
    return {"message": "LigBind Backend Running Successfully"}

@app.get("/db-test")
def db_test():
    collections = db.list_collection_names()
    return {
        "status": "MongoDB Connected",
        "collections": collections
    }