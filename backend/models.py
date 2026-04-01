from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)          # URL-safe slug: "covers"
    display_name = Column(String(200), nullable=False)               # Human-readable: "Phone Cases"
    image_folder = Column(String(200), nullable=False)               # e.g. "covers"
    image_prefix = Column(String(100), nullable=False)               # e.g. "phonecover"
    image_ext = Column(String(20), nullable=False, default=".jpg.jpeg")
    has_device_option = Column(Boolean, default=False)               # +₹50 standard/premium selector
    device_premium_label = Column(String(200), default="iPhone / Samsung S series")
    device_premium_extra = Column(Integer, default=50)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    price = Column(Integer, nullable=False)                          # Price in ₹
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    image_path = Column(String(500), nullable=True)                  # Relative path or full URL
    has_size_option = Column(Boolean, default=False)                 # +₹20 small/big selector
    size_premium_extra = Column(Integer, default=20)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
