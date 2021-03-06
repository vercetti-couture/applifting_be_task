"Creating a database models"
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from .db import Base




class Offer(Base):
    "Creating model for Offer API"
    __tablename__ = 'offers'
    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float(precision=2), nullable=True)
    items_in_stock = Column(Integer, nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)   
    def __repr__(self):
        return f'OfferModel(price={self.price}, items_in_stock={self.items_in_stock}, id={self.id})'

class Product(Base):
    "Creating model for Product API"
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False, unique=True, index=True)
    description = Column(String(255))
    offers =  relationship('Offer',
                            cascade='all, delete-orphan')
    prices = relationship('PriceLogs', cascade='all, delete-orphan')
    def __repr__(self):
        return f'ProductModel(name={self.name}, '

class PriceLogs(Base):
    "Creating model to track price history"
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float)
    time = Column(Float(precision=2), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)


class User(Base):
    "Creating model to store Users "
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,index=True)
    username = Column(String(32), nullable=False, unique=True, index=True)
    password = Column(String(64), nullable=False)
    def __repr__(self):
        return f'UsersModel(username={self.username})'
