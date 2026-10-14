from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from controller.avia_controller import router as avia_router

app = FastAPI(title="Avia Metrics API")

app.include_router(avia_router)



