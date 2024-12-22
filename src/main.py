from fastapi import FastAPI
from routes import router as rt

app = FastAPI()

app.include_router(rt)
