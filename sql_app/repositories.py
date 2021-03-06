"Creating functions to interacte with the data in the database"
import random
from sqlalchemy.orm import Session
from . import models, schemas
#pylint: disable=no-self-argument
#pylint: disable=no-member

class OfferRepo:
    "Creating CRUD operations for Offers API model"
    def create(db: Session, offer: schemas.OfferCreate):
        "Create Offer in DataBase"
        db_offer = models.Offer(product_id=offer.product_id)
        db.add(db_offer)
        db.commit()
        db.refresh(db_offer)
        return db_offer
        
    def fetch_by_id(db: Session, _id:int):
        "Select Offer by ID from DataBase"
        return db.query(models.Offer).filter(models.Offer.id == _id).first()
 
    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
        "Select all Offers from DataBase"
        return db.query(models.Offer).offset(skip).limit(limit).all()
    
    def delete(db: Session,_id:int):
        "Delete Offer with given ID from DataBase"
        db_product = db.query(models.Offer).filter_by(id=_id).first()
        db.delete(db_product)
        db.commit()
        
    def update(db: Session, offer_data):
        "Update Offer with given ID in Database"
        updated_product = db.merge(offer_data)
        db.commit()
        return updated_product

    def select_random_offer(db: Session):
        "Select random Offer from DataBase"
        offers = OfferRepo.fetch_all(db=db)
        if offers:
            random_offer = random.choice(offers)
            return random_offer
        return False

class ProductRepo:
    "Creating CRUD operations for Products API model"
    def create(db: Session, product: schemas.ProductCreate):
        "Create product in DataBase"
        db_product = models.Product(name=product.name,description=product.description)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product           
    
    def fetch_by_id(db: Session, _id):
        "Select Product by ID from DataBase"
        return db.query(models.Product).filter(models.Product.id == _id).first()
 
    def fetch_by_name(db: Session,name):
        "Select Product by Name from DataBase"
        return db.query(models.Product).filter(models.Product.name == name).first()
 
    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
        "Select all Products from DataBase"
        return db.query(models.Product).offset(skip).limit(limit).all()
 
    def delete(db: Session,product_id):
        "Delete Product with given ID from DataBase"
        db_product = db.query(models.Product).filter_by(id=product_id).first()
        db.delete(db_product)
        db.commit()    
    
    def update(db: Session,product_data):
        "Update Product with given ID in Database"
        updated_product = db.merge(product_data)
        db.commit()
        return updated_product
    
class UserRepo:
    "Creating CRUD operations for Users model"
    def create(db: Session, username: schemas.RegisterUser, password: schemas.RegisterUser):
        "Create user in DataBase"
        db_user = models.User(username=username,password=password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def fetch_by_name(db: Session, username):
        "Select User by username from DataBase"
        return db.query(models.User).filter(models.User.username == username).first()

class PriceRepo:
    "Creating operations for Price Model"
    def get_price_history(db: Session, product_id):
        """Returns a list of prices for the specified product_id"""
        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        price_history = []
        if db_product:
            for price in db_product.prices:
                price_history.append(price.price)
            return price_history
        return False
    
    def get_price_change(db: Session, from_time, to_time, product_id):
        """Returns a percentage changes for the specified product_id and time"""
        db_product = db.query(models.PriceLogs).filter(models.PriceLogs.product_id == product_id).first()
        if db_product:
            first_date = db.query(models.PriceLogs).filter(models.PriceLogs.time == from_time).first().price
            last_date = db.query(models.PriceLogs).filter(models.PriceLogs.time == to_time).first().price
            if first_date and last_date:
                return round(((last_date-first_date)/first_date) * 100, 1)
        return False
