from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Category, Admin
from ..schemas import CategoryCreate, CategoryUpdate, CategoryResponse, StoreCategoryResponse, ProductResponse
from ..auth import get_current_admin

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Fetch all categories ordered by sort_order."""
    return db.query(Category).order_by(Category.sort_order, Category.id).all()


@router.get("/with-products", response_model=List[StoreCategoryResponse])
def get_categories_with_products(db: Session = Depends(get_db)):
    """Fetch all categories with their products — used by the storefront."""
    categories = db.query(Category).options(
        joinedload(Category.products)
    ).order_by(Category.sort_order, Category.id).all()
    result = []
    for cat in categories:
        sorted_products = sorted(cat.products, key=lambda p: (p.sort_order, p.id))
        products_data = []
        for p in sorted_products:
            products_data.append({
                **{c.name: getattr(p, c.name) for c in p.__table__.columns},
                "category_name": cat.name,
                "category_display_name": cat.display_name,
            })
        cat_dict = {c.name: getattr(cat, c.name) for c in cat.__table__.columns}
        cat_dict["products"] = products_data
        result.append(cat_dict)
    return result


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = db.query(Category).filter(
            Category.name == update_data["name"], Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already taken")

    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
