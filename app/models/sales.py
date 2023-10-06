from datetime import datetime
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime,ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('inventory_items.id'))
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow)