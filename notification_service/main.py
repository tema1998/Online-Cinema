import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware.sessions import SessionMiddleware

from notification_service.api.v1.dependencies import (
    set_pika_connection,
    close_pika_connection,
)
from notification_service.api.v1.endpoints.messages import router as messages_router
from notification_service.api.v1.endpoints.periodic_messages import (
    router as periodic_messages_router,
)
from notification_service.config.scheduler_settings import scheduler
from notification_service.config.settings import settings

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await set_pika_connection()
    yield
    await close_pika_connection()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

scheduler.start()

origins = ["http://localhost",
           "http://localhost:8080", "http://127.0.0.1:8080"]

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware
app.add_middleware(SessionMiddleware,
                   secret_key=settings.middleware_secret_key)


app.include_router(messages_router, prefix="/api/v1",
                   tags=["instant_messages"])
app.include_router(
    periodic_messages_router, prefix="/api/v1", tags=["periodic_messages"]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
