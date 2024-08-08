import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import models
import database
import endpoints

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Creating tables in database")
    async with database.engine.begin() as connection:
        await connection.run_sync(database.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(endpoints.router)

uvicorn.run(app, host="0.0.0.0", port=models.settings.port)
