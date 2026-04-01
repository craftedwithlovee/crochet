from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


# ── Category ──────────────────────────────────────────────────────────────────

class CategoryBase(BaseModel):
    name: str
    display_name: str
    image_folder: str
    image_prefix: str
    image_ext: str = ".jpg.jpeg"
    has_device_option: bool = False
    device_premium_label: str = "iPhone / Samsung S series"
    device_premium_extra: int = 50
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    image_folder: Optional[str] = None
    image_prefix: Optional[str] = None
    image_ext: Optional[str] = None
    has_device_option: Optional[bool] = None
    device_premium_label: Optional[str] = None
    device_premium_extra: Optional[int] = None
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Product ───────────────────────────────────────────────────────────────────

class ProductBase(BaseModel):
    name: str
    price: int
    category_id: int
    image_path: Optional[str] = None
    has_size_option: bool = False
    size_premium_extra: int = 20
    sort_order: int = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    category_id: Optional[int] = None
    image_path: Optional[str] = None
    has_size_option: Optional[bool] = None
    size_premium_extra: Optional[int] = None
    sort_order: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    category_name: Optional[str] = None
    category_display_name: Optional[str] = None

    class Config:
        from_attributes = True


# ── Admin / Auth ──────────────────────────────────────────────────────────────

class AdminLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class AdminCredentialsUpdate(BaseModel):
    current_password: str
    new_username: Optional[str] = None
    new_password: Optional[str] = None


# ── Aggregated store response ─────────────────────────────────────────────────

class StoreCategoryResponse(CategoryResponse):
    """Category with its products included — used by the storefront."""
    products: List[ProductResponse] = []
