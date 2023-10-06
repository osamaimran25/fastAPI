from fastapi import FastAPI
from api.routes.inventory import inventory_router
from api.routes.sales import sales_router
app = FastAPI()

# Define a route and a function to handle it
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

app.include_router(inventory_router)
app.include_router(sales_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
