from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey, Column, Integer, String
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='restaurant')
    # Relationship with RestaurantPizza
    restaurant_pizzas = relationship(
        "RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan"
    )

    # Association proxy for pizzas through RestaurantPizza
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    serialize_rules = ("-restaurant_pizzas.restaurant",)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model):
    __tablename__ = 'pizzas'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = Column(String)
    restaurant_pizzas = relationship('RestaurantPizza', back_populates='pizza')
    serialize_rules = ("-restaurants.pizzas",)

    def __repr__(self):
        return f"<Pizza {self.name}>"


class RestaurantPizza(db.Model):
    __tablename__ = 'restaurant_pizzas'

    id = Column(Integer, primary_key=True)
    price = Column(Integer)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    pizza_id = Column(Integer, ForeignKey('pizzas.id'))
    restaurant = relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = relationship('Pizza', back_populates='restaurant_pizzas')

    # Validation for price
    @validates("price")
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurants")

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
