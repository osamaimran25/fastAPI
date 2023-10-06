from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base


class InventoryItem(Base):
    __tablename__ = 'inventory_items'

    id = Column(Integer, primary_key=True, index=True)  # Index added
    name = Column(String, nullable=False)
    description = Column(String)
    quantity = Column(Integer, default=0, index=True)  # Index added
    price = Column(DECIMAL(10, 2), nullable=False)
    low_stock_threshold = Column(Integer, default=10)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)  
    category = relationship('Category', back_populates='items')

    @property
    def current_inventory_status(self):
        if self.quantity == 0:
            return "Out of Stock"
        elif self.quantity < self.low_stock_threshold:
            return "Low Stock"
        else:
            return "In Stock"

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    items = relationship('InventoryItem', back_populates='category')