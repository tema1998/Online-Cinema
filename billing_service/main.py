from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware.sessions import SessionMiddleware

from api.v1.order import router as order_router
from core.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=config.billing_project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

origins = ["http://localhost", "http://localhost:8000", "http://127.0.0.1:8000"]

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

app.include_router(
    order_router, prefix="/api/v1/order", tags=["order"]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
