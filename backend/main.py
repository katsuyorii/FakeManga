from fastapi import FastAPI

from auth.routers import auth_router


app = FastAPI()

app.include_router(auth_router)