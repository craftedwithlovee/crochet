from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Product, Category, Admin
from ..schemas import ProductCreate, ProductUpdate, ProductResponse
from ..auth import get_current_admin

router = APIRouter(prefix="/api/products", tags=["Products"])


def _to_response(p: Product) -> dict:
    """Convert a Product ORM object to a response dict with category info."""
    return {
        **{c.name: getattr(p, c.name) for c in p.__table__.columns},
        "category_name": p.category.name if p.category else None,
        "category_display_name": p.category.display_name if p.category else None,
    }


@router.get("", response_model=List[ProductResponse])
def get_products(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Fetch all products, optionally filtered by category."""
    q = db.query(Product).order_by(Product.sort_order, Product.id)
    if category_id:
        q = q.filter(Product.category_id == category_id)
    products = q.all()
    return [_to_response(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return _to_response(p)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    # Verify category exists
    cat = db.query(Category).filter(Category.id == data.category_id).first()
    if not cat:
        raise HTTPException(status_code=400, detail="Category not found")

    # Auto-generate image path if not provided
    image_path = data.image_path
    if not image_path:
        # Find next sort order
        max_sort = db.query(Product).filter(
            Product.category_id == data.category_id
        ).count() + 1
        image_path = f"images/{cat.image_folder}/{cat.image_prefix}{max_sort}{cat.image_ext}"

    product = Product(
        name=data.name,
        price=data.price,
        category_id=data.category_id,
        image_path=image_path,
        has_size_option=data.has_size_option,
        size_premium_extra=data.size_premium_extra,
        sort_order=data.sort_order or (db.query(Product).filter(
            Product.category_id == data.category_id
        ).count() + 1),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return _to_response(product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = data.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        cat = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not cat:
            raise HTTPException(status_code=400, detail="Category not found")

    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return _to_response(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
