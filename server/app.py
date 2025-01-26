#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
import os
from models import db, Restaurant, RestaurantPizza, Pizza

# Configure the database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize database and migrations
migrate = Migrate(app, db)
db.init_app(app)

# Initialize Flask-RESTful API
api = Api(app)

# Routes and Resources
@app.route("/")
def index():
    return "<h1>Code Challenge</h1>"


class Restaurants(Resource):
    def get(self):
        """Retrieve all restaurants."""
        restaurants = Restaurant.query.all()
        response = [
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
            }
            for restaurant in restaurants
        ]
        return make_response(jsonify(response), 200)


class RestaurantByID(Resource):
    def get(self, id):
        """Retrieve a single restaurant by its ID."""
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

        response = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "price": rp.price,
                    "pizza": {
                        "id": rp.pizza.id,
                        "name": rp.pizza.name,
                        "ingredients": rp.pizza.ingredients,
                    },
                }
                for rp in restaurant.restaurant_pizzas
            ],
        }
        return make_response(jsonify(response), 200)

    def delete(self, id):
        """Delete a restaurant by its ID."""
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)


class Pizzas(Resource):
    def get(self):
        """Retrieve all pizzas."""
        pizzas = Pizza.query.all()
        response = [
            {"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients}
            for pizza in pizzas
        ]
        return make_response(jsonify(response), 200)


class RestaurantPizzas(Resource):
    def post(self):
        """Create a new RestaurantPizza."""
        data = request.get_json()
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        # Validate price range
        if not (1 <= price <= 30):
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        try:
            restaurant_pizza = RestaurantPizza(
                price=price, pizza_id=pizza_id, restaurant_id=restaurant_id
            )
            db.session.add(restaurant_pizza)
            db.session.commit()

            response = {
                "id": restaurant_pizza.id,
                "price": restaurant_pizza.price,
                "pizza_id": restaurant_pizza.pizza_id,
                "restaurant_id": restaurant_pizza.restaurant_id,
                "pizza": {
                    "id": restaurant_pizza.pizza.id,
                    "name": restaurant_pizza.pizza.name,
                    "ingredients": restaurant_pizza.pizza.ingredients,
                },
                "restaurant": {
                    "id": restaurant_pizza.restaurant.id,
                    "name": restaurant_pizza.restaurant.name,
                    "address": restaurant_pizza.restaurant.address,
                },
            }
            return make_response(jsonify(response), 201)
        except Exception as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)


# Add resources to the API
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
