import random
from datetime import datetime
from models.inventory import InventoryItem, Category  
from database import Session, engine, Base
from models.sales import Sale
from models.inventory import InventoryItem

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
from datetime import datetime, timedelta

session=Session(bind=engine)
fake = Faker()
Base.metadata.create_all(bind=engine)

categories = [Category(name=fake.word()) for _ in range(5)]
session.add_all(categories)
session.commit()

for _ in range(100):
    item = InventoryItem(
        name=fake.word(),
        description=fake.sentence(),
        quantity=random.randint(1, 100),
        price=random.uniform(1.0, 100.0),
        low_stock_threshold = random.choice([10,1,15,10,5,3]),
        category=random.choice(categories)
    )
    session.add(item)

session.commit()


num_records = 300

start_date = datetime.utcnow() - timedelta(days=365)
end_date = datetime.utcnow()
sales = session.query(Sale).all()
for _ in range(num_records):
    item_id = random.randint(1, 100)  
    quantity = random.randint(1, 10)  
    price = round(random.uniform(10, 1000), 2)
    sale_date = start_date + timedelta(days=random.randint(0, 365))


    sale = Sale(item_id=item_id, quantity=quantity, price=price, sale_date=sale_date)
    session.add(sale)
session.commit()
