from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select , update
from sqlalchemy.orm import Session

from app.db_depends import get_db
from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas import Product as ProductSchema, ProductCreate

router = APIRouter(
    prefix="/products",
    tags = ["products"],
)

@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: Session = Depends(get_db)):
    """
    Возвращает список всех активных товаров.
    """
    stmt = select(ProductModel).where(ProductModel.is_active == True)
    products = db.scalars(stmt).all()
    return products

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(pr_cr: ProductCreate, db: Session = Depends(get_db)):
    """
    Создаёт новый товар.
    """
    # проверка что существует category_id
    stmt = select(CategoryModel).where(
        CategoryModel.id == pr_cr.category_id,
        CategoryModel.is_active == True,
    )
    category = db.scalars(stmt).first()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found"
        )

    product = ProductModel(**pr_cr.model_dump(), is_active=True)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/category/{category_id}",response_model=list[ProductSchema])
async def get_products_by_category(category_id: int,db: Session = Depends(get_db)) -> list[ProductModel]:
    stmt = select(CategoryModel).where(CategoryModel.id  == category_id,CategoryModel.is_active == True)
    category = db.scalars(stmt).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Category not found or inactive")
    stmt1 = select(ProductModel).where(ProductModel.category_id  == category_id, ProductModel.is_active == True)
    
    return db.scalars(stmt1).all()

@router.get("/{product_id}",response_model=ProductSchema)
async def get_product(product_id: int,db: Session = Depends(get_db)) -> ProductModel:
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    prod = select(ProductModel).where(ProductModel.id == product_id,ProductModel.is_active == True)
    product = db.scalars(prod).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found or inactive")
    return product

@router.put("/{product_id}",response_model=ProductSchema)
async def update_product(product_id: int,pr_up: ProductCreate, db: Session = Depends(get_db)) -> ProductModel:
    """
    Обновляет товар по его ID.
    """
    data = pr_up.model_dump()
    stmt = select(ProductModel).where(ProductModel.id == product_id,ProductModel.is_active == True)
    product = db.scalars(stmt).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found or inactive")

    if data["category_id"] != product.category_id:
        category_stmt = select(CategoryModel).where(
            CategoryModel.id == data["category_id"],
            CategoryModel.is_active == True,
        )
        category = db.scalars(category_stmt).first()
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found or inactive",
            )

    for field in ("name", "description", "price", "image_url", "stock", "category_id"):
        setattr(product, field, data[field])

    db.commit()
    db.refresh(product)    
    return product

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Логически удаляет товар по его ID (is_active=False).
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    product = db.scalars(stmt).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive"
        )
    
    db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(is_active=False)
    )
    
    db.commit()
    return {"status":"success", "message": "Product marked as inactive"}
