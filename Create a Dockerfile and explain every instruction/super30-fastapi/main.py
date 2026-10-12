import os 
from fastapi import FastAPI

app = FastAPI(title="Super30 API")

APPNAME = os.getenv("APPNAME", "Super30 API") 
APPENV = os.getenv("APPENV", "development")

@app.get("/") 
def home(): 
    return { "message": f"Welcome to {APPNAME}!", "environment": APPENV }

@app.get("/config") 
def config(): 
    return { "appname": APPNAME, "environment": APP_ENV }

@app.get("/health") 
def health(): 
    return {"status": "healthy"}