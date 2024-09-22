import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
import database
import routes

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Creating tables in database")
    async with database.engine.begin() as connection:
        await connection.run_sync(database.Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(routes.router)

if models.settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=models.settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

uvicorn.run(app, host="0.0.0.0", port=models.settings.PORT)
