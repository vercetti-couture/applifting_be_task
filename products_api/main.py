'Products API'
import sys
import os
import logging
import json
from typing import List, Optional
import requests
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi_utils.tasks import repeat_every
import uvicorn
from sqlalchemy.orm import Session
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# pylint: disable=import-error
# pylint: disable=wrong-import-position
from sql_app import models
from sql_app.db import get_db, engine, SessionLocal
from sql_app import schemas
from sql_app.repositories import ProductRepo, OfferRepo
from settings import API_KEY


app = FastAPI(title="Sample FastAPI Application",
              description="Sample FastAPI Application with Swagger and Sqlalchemy",
              version="1.0.0",)
logging.basicConfig(level=logging.DEBUG)
OFFERS_API_URL = os.getenv("OFFERS_API_URL", '127.0.0.1:9000')

models.Base.metadata.create_all(bind=engine)

token = requests.post(f'http://{OFFERS_API_URL}/token',
                      data=json.dumps({'api_key': API_KEY})).json()['token']


@app.on_event("startup")
@repeat_every(seconds=60)
def get_last_offer():
    "Background service to set price fo offers"
    db_session = SessionLocal()
    last_offer = OfferRepo.fetch_all(db_session)[-1]

    logging.info('New/Updated offer is: id=%s, items_in_stock=%s, price=%s',
    last_offer.id, last_offer.items_in_stock, last_offer.price)



@app.exception_handler(Exception)
def validation_exception_handler(request, err):
    "Global exception handler"
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}.Detail: {err}"})


@app.post('/products', tags=["Product"], response_model=schemas.Product, status_code=201)
def create_product(product_request: schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    Create an Product and store it in the database
    """
    db_product = ProductRepo.fetch_by_name(db, name=product_request.name)
    if db_product:
        raise HTTPException(status_code=400, detail="Product already exists!")
    new_product = ProductRepo.create(db=db, product=product_request)  
    requests.post(f'http://{OFFERS_API_URL}/products/register', data=json.dumps(
            {'product_id': new_product.id,
            'token': token
            }
        ))

    return new_product

    

@app.get('/products', tags=["Product"], response_model=List[schemas.Product])
def get_all_products(name: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get all the Products stored in database
    """
    if name:
        products = []
        db_product = ProductRepo.fetch_by_name(db, name)
        products.append(db_product)
        return products
    else:
        return ProductRepo.fetch_all(db)


@app.get('/products/{product_id}', tags=["Product"], response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get the Product with the given ID provided by User stored in database
    """
    db_product = ProductRepo.fetch_by_id(db, product_id)
    if db_product is None:
        raise HTTPException(
            status_code=404, detail="Product not found with the given ID")
    return db_product


@app.delete('/products/{product_id}', tags=["Product"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Delete the Product with the given ID provided by User stored in database
    """
    db_product = ProductRepo.fetch_by_id(db, product_id)
    if db_product is None:
        raise HTTPException(
            status_code=404, detail="Product not found with the given ID")
    ProductRepo.delete(db, product_id)
    return {'message': f'Product with id {product_id} was successfully deleted'}


@app.put('/products/{product_id}', tags=["Product"], response_model=schemas.Product)
def update_product(product_id: int,product_request: schemas.Product, db: Session = Depends(get_db)):
    """
    Update an Product stored in the database
    """
    db_product = ProductRepo.fetch_by_id(db, product_id)
    if db_product:
        update_item_encoded = jsonable_encoder(product_request)
        db_product.name = update_item_encoded['name']
        db_product.description = update_item_encoded['description']       
        return ProductRepo.update(db=db, product_data=db_product)
    else:
        raise HTTPException(
            status_code=400, detail="Product not found with the given ID")


