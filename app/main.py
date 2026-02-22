from contextlib import asynccontextmanager

from fastapi import FastAPI
from app import models  # noqa: F401
from app.database import Base, async_engine
from app.routers import categories, products, reviews, users, cart


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Auto-create tables for local start without manual migration step.
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="FastAPI интернет-магазин",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(users.router)
app.include_router(cart.router)


@app.get("/")
async def root():
    return {"mesages": "Добро пожаловать в API интрнет-магазин!"}
