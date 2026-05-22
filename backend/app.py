from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.predict_route import router

import os

# -----------------------------
# CREATE FOLDERS
# -----------------------------
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI()

# -----------------------------
# HOME ROUTE
# -----------------------------
@app.get("/")
def home():
    return {"message": "OSCC Backend Running"}

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# API ROUTES
# -----------------------------
app.include_router(
    router,
    prefix="/api/v1"
)

# -----------------------------
# SERVE OUTPUT IMAGES
# -----------------------------
app.mount(
    "/outputs",
    StaticFiles(directory="outputs"),
    name="outputs"
)

# -----------------------------
# SERVE UPLOADED IMAGES (OPTIONAL)
# -----------------------------
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)