from fastapi import FastAPI
from contextlib import asynccontextmanager

import logging

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware.sessions import SessionMiddleware

from notification_gen_app.api.v1.dependencies import set_pika_connection, close_pika_connection
from notification_gen_app.api.v1.endpoints.messages import router as messages_router
from notification_gen_app.api.v1.endpoints.periodic_messages import router as periodic_messages_router
from notification_gen_app.config.initialization import initialize_rabbitmq
from notification_gen_app.config.scheduler_settings import scheduler
from notification_gen_app.config.settings import settings

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('RabbitMQ initialization')
    await initialize_rabbitmq()
    logging.info('RabbitMQ initialization complete')
    await set_pika_connection()
    yield
    await close_pika_connection()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

scheduler.start()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.middleware_secret_key
)

#
# @app.middleware('http')
# async def before_request(request: Request, call_next):
#     request_id = request.headers.get('X-Request-Id')
#
#     if not request_id:
#         return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
#
#     response = await call_next(request)
#     return response


app.include_router(messages_router, prefix='/api/v1', tags=['instant_messages'])
app.include_router(periodic_messages_router, prefix='/api/v1', tags=['periodic_messages'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
