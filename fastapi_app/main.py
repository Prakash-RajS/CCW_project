from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_app.routes.auth import router as auth_router
from fastapi_app.routes.creator import router as creator_router
from fastapi_app.routes.collaborator import router as collaborator_router 
from fastapi_app.routes.my_profile import router as my_profile_router 

app = FastAPI()

# CORS (optional if you already added)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REGISTER ROUTES
app.include_router(auth_router)
app.include_router(creator_router)
app.include_router(collaborator_router) 
app.include_router(my_profile_router)




@app.get("/")
def home():
    return {"message": "Welcome to CCW FastAPI"}
