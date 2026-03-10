from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401
from app.config import AUTO_CREATE_TABLES
from app.database import Base, async_engine
from app.routers import cart, categories, orders, payments, products, reviews, users

from loguru import logger
from uuid import uuid4
from fastapi import Request
from fastapi.responses import JSONResponse


logger.add("info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message}]", level="INFO", enqueue = True)

@asynccontextmanager
async def lifespan(_: FastAPI):
    if AUTO_CREATE_TABLES:
        # Optional for local dev only. In production use Alembic migrations.
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="FastAPI интернет-магазин",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_id = str(uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to {request.url.path} failed")
            else:
                logger.info('Successfully accessed ' + request.url.path)
        except Exception as ex:
            logger.error(f"Request to {request.url.path} failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)
        return response

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(users.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)

app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в API интернет-магазина!"}
