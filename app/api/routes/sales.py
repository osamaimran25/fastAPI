import logging
from typing import List
from fastapi import Query, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import  func
from datetime import datetime, timedelta, date

from schemas import SaleQueryParams
from models.inventory import InventoryItem, Category
from models.sales import Sale 
from database import get_db_session 

logger = logging.getLogger(__name__)

sales_router = APIRouter(prefix='/sales',tags=['sales'])


@sales_router.get("/")
async def get_sales(
    params: SaleQueryParams = Depends(),
    db: Session = Depends(get_db_session)):  
    try:
        query = db.query(Sale, InventoryItem, Category). \
            join(InventoryItem, Sale.item_id == InventoryItem.id). \
            join(Category, InventoryItem.category_id == Category.id). \
            filter(Sale.sale_date >= params.start_date, Sale.sale_date <= params.end_date)
        
        if params.item_id:
            query = query.filter(Sale.item_id == params.item_id)

        if params.category_id:
            query = query.filter(InventoryItem.category_id == params.category_id)
        
        results = query.all()
        sales_data = []
        for sale, item, category in results:
            sales_data.append({
                "sale_id": sale.id,
                "quantity": sale.quantity,
                "price": sale.price,
                "sale_date": sale.sale_date,
                "item_name": item.name,
                "category_name": category.name
            })
        return sales_data
    except Exception as e:
        logger.error(f"Error fetching sales data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@sales_router.get("/revenue")
async def get_sales_analysis(db: Session = Depends(get_db_session),
                             interval: str = Query("daily", description="Time interval (daily, weekly, monthly, annual)"),category_id: int = Query(None, description="Category ID for filtering"),item_id: int = Query(None, description="Item ID for filtering"),):
    try:
        today = datetime.now()

        if interval == "daily":
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif interval == "weekly":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
        elif interval == "monthly":
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = (today.replace(day=28, hour=23, minute=59, second=59, microsecond=999999) +
                        timedelta(days=(31 - today.day)))
        elif interval == "annual":
            start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)

        total_sales = db.query(func.sum(Sale.price * Sale.quantity)).filter(
            Sale.sale_date.between(start_date, end_date)
        ).scalar() or 0
        return {"interval": interval, "sales": total_sales}
    except Exception as e:
        logger.error(f"Error fetching sales data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@sales_router.get("/custom-sales-data")
async def get_sales_with_differet_filters(db: Session = Depends(get_db_session), category_id: int = Query(None), item_id: int = Query(None),
    start_date: str = Query(None), end_date: str = Query(None),
):
    try:
        query = db.query(Sale)
        if category_id:
            query = query.join(InventoryItem).filter(InventoryItem.category_id == category_id)
        if item_id:
            query = query.filter(Sale.item_id == item_id)
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Sale.sale_date <= end_date)
        total_sales = query.with_entities(func.sum(Sale.quantity * Sale.price)).scalar() or 0
        db.close()

        return {"total_sales": total_sales}
    except Exception as e:
        logger.error(f"Error fetching sales data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")