from fastapi import FastAPI
from app.routers import categories, products, reviews, users
from uvicorn import run

app = FastAPI(
    title="FastAPI интернет-магазин",
    version="0.1.0"
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(reviews.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"mesages": "Добро пожаловать в API интрнет-магазин!"}


