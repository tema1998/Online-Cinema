from contextlib import asynccontextmanager

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from starlette.middleware.sessions import SessionMiddleware

from core.config import config
from api.v1.subscription import router as subscription_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield

app = FastAPI(
    title=config.billing_project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
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
    secret_key=config.secret_key  # Ensure this is a strong, random secret key
)

#TODO: Turn on middleware on prod.

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

app.include_router(subscription_router, prefix='/api/v1/subscription', tags=['subscription'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
