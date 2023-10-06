import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List 

from database import Session, engine, get_db_session
from models.inventory import InventoryItem, Category
from schemas import InventoryItemResponse, InventoryCreateItem

logger = logging.getLogger(__name__)

inventory_router = APIRouter(prefix='/inventory',tags=['inventory'])

@inventory_router.post("/", response_model=InventoryCreateItem)
def create_item(item: InventoryCreateItem, db: Session = Depends(get_db_session)):
    try:
        # Create an instance of the SQLAlchemy model using the data from the Pydantic model
        db_item = InventoryItem(**item.dict())

        # Add the instance to the session and commit
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        return db_item  # Return the SQLAlchemy model instance
    except Exception as e:
        logger.error(f"failed to create item {item}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@inventory_router.get("/",  response_model=List[InventoryItemResponse])
async def get_inventory(page: int = Query(default=1, ge=1), per_page: int = Query(default=10, ge=1),db: Session = Depends(get_db_session)):
    try:
        inventory_with_category = db.query(InventoryItem).join(InventoryItem.category)

        total_inventory = inventory_with_category.count()
        paginated_inventory = inventory_with_category.limit(per_page).offset((page - 1) * per_page).all()
        
        inventory_item_response = [InventoryItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            quantity=item.quantity,
            price=item.price,
            created_at=str(item.created_at),
            updated_at=str(item.updated_at),
            category={
                    'id': item.category.id,
                    'name': item.category.name
                },
            low_stock_threshold=item.low_stock_threshold,
            status=item.current_inventory_status
        ) for item in paginated_inventory]
        return inventory_item_response  
    
    except Exception as e:
        logger.error(f"Error fetching inventory data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@inventory_router.put("/{item_id}")
async def update_inventory(item_id: int, quantity_change: int, db: Session = Depends(get_db_session)):
    try:
        item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        # Update the quantity and save the change to the database
        item.quantity = quantity_change
        db.commit()
        db.refresh(item)

        return {"message": "Inventory updated successfully", "new_quantity": item.quantity, "updated_at":item.updated_at}
    except Exception as e:
        logger.error(f"failed to update {item_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
