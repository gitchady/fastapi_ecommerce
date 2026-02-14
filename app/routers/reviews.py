from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.auth import get_current_user
from app.db_depends import get_async_db
from app.models.products import Product as ProductModel
from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.schemas import Review as ReviewSchema, ReviewCreate

router = APIRouter()


async def update_product_rating(db: AsyncSession, product_id: int) -> float:
    avg_rating = await db.scalar(
        select(func.coalesce(func.avg(ReviewModel.grade), 0.0)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True,
        )
    )
    product = await db.get(ProductModel, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    product.rating = float(avg_rating or 0.0)
    return product.rating


@router.get("/reviews/", response_model=list[ReviewSchema])
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных отзывов.
    """
    stmt = select(ReviewModel).where(ReviewModel.is_active == True)
    db_stmt = await db.scalars(stmt)
    review_db_stmt = db_stmt.all()
    return review_db_stmt


@router.get("/products/{product_id}/reviews/", response_model=list[ReviewSchema])
async def get_product_reviews(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список активных отзывов для конкретного товара.
    """
    product_db_stmt = select(ProductModel).where(
        ProductModel.is_active == True,
        ProductModel.id == product_id,
    )
    product_db_result = await db.scalars(product_db_stmt)
    product = product_db_result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    review_db_stmt = select(ReviewModel).where(
        ReviewModel.is_active == True,
        ReviewModel.product_id == product_id,
    )
    review_db_result = await db.scalars(review_db_stmt)
    reviews = review_db_result.all()
    return reviews


@router.post("/reviews/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    cr_review: ReviewCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Создаёт новый отзыв, привязанный к текущему товару (только для buyer).
    """
    if current_user.role != "buyer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role must be buyer")
    if cr_review.grade < 1 or cr_review.grade > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Grade must be between 1 and 5",
        )

    product_result = await db.scalars(
        select(ProductModel).where(
            ProductModel.id == cr_review.product_id,
            ProductModel.is_active == True,
        )
    )
    product = product_result.first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    review = ReviewModel(
        user_id=current_user.id,
        **cr_review.model_dump(),
    )
    db.add(review)
    await db.flush()
    await update_product_rating(db, cr_review.product_id)
    await db.commit()
    await db.refresh(review)
    return review


@router.delete("/reviews/{review_id}", response_model=ReviewSchema)
async def delete_review(
    review_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Выполняет мягкое удаление отзыва.
    Доступно только admin или seller товара, к которому относится отзыв.
    """
    review_result = await db.scalars(
        select(ReviewModel).where(
            ReviewModel.is_active == True,
            ReviewModel.id == review_id,
        )
    )
    review = review_result.first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    # Разрешено: admin или seller товара, к которому относится отзыв.
    if current_user.role != "admin":
        if current_user.role != "seller":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin or product seller can delete review",
            )

        product = await db.get(ProductModel, review.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if product.seller_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin or product seller can delete review",
            )

    review.is_active = False
    await db.flush()
    await update_product_rating(db, review.product_id)
    await db.commit()
    await db.refresh(review)
    return review
