from contextlib import asynccontextmanager

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from starlette.middleware.sessions import SessionMiddleware

from src.core.config import config
from src.db.redis_db import get_redis, init_redis
from src.api.auth import router as auth_router
from src.api.roles import router as roles_router
from src.api.premium import router as premium_router
from src.utils.limit_of_requests import check_limit_of_requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Redis initialization
    await init_redis()  # Initialize the Redis connection
    redis = await get_redis()  # Get the Redis client instance
    await redis.ping()  # Check if the Redis connection is working
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    yield

    # Shutdown: close Redis connection, drop tables
    await redis.close()


def configure_tracer() -> None:
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create(
            {SERVICE_NAME: "auth-service"}))
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=config.jaeger_host, agent_port=config.jaeger_port
            )
        )
    )


if config.enable_tracer:
    configure_tracer()

app = FastAPI(
    title=config.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

FastAPIInstrumentor.instrument_app(app)

origins = [
    "http://localhost",
    "http://localhost:80",
    "http://127.0.0.1:80",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Add CORS middleware for handling cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add SessionMiddleware for handling OAuth session state
app.add_middleware(
    SessionMiddleware,
    secret_key=config.secret_key,  # Ensure this is a strong, random secret key
)

tracer = trace.get_tracer(__name__)
# @app.middleware('http')
# async def before_request(request: Request, call_next):
#
#     user_ip = request.headers.get('X-Forwarded-For')
#     request_id = request.headers.get('X-Request-Id')
#     request_url = str(request.url)
#
#     if not request_id:
#         return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
#
#     result_of_checking_limit_of_requests = await check_limit_of_requests(user_ip=user_ip)
#     if result_of_checking_limit_of_requests:
#         return ORJSONResponse(
#             status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#             content={'detail': 'Too many requests'}
#         )
#     if config.enable_tracer:
#         with tracer.start_as_current_span(request_url) as span:
#             span.set_attribute('http.request_id', request_id)
#             response = await call_next(request)
#     else:
#         response = await call_next(request)
#
#     return response

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roles_router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(premium_router, prefix="/api/v1/premium", tags=["premium"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
