from fastapi import FastAPI

app = FastAPI(title="Super30 API")

@app.get("/") 
def home(): 
    return {"message": "Welcome to Super30 FastAPI!"}

@app.get("/hello") 
def hello(): 
    return {"message": "Hello from Dockerized FastAPI!"}

@app.get("/health") 
def health(): 
    return {"status": "healthy"}