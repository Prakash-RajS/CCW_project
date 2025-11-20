from fastapi import FastAPI
from fastapi_app.routes import auth

app = FastAPI(title="CCW FastAPI")

# Register Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def home():
    return {"message": "CCW FastAPI is running 🚀"}
