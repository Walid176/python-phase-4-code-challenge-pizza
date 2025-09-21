#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_all_restaurants():
    restaurants = Restaurant.query.all()
    
    data = [
        {
            "id": r.id,
            "name": r.name,
            "address": r.address
        }
        for r in restaurants
    ]

    return jsonify(data), 200


@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    
    data = restaurant.to_dict()

    data["restaurant_pizzas"] = [
        {
            "id": rp.id,
            "price": rp.price,
            "restaurant_id": rp.restaurant_id,
            "pizza_id": rp.pizza_id,
            "pizza": {
                "id": rp.pizza.id,
                "name": rp.pizza.name,
                "ingredients": rp.pizza.ingredients
            }
        }
        for rp in restaurant.pizzas
    ]

    return jsonify(data), 200

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    
    db.session.delete(restaurant)
    db.session.commit()

    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    data = [
        {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        }
        for pizza in pizzas
    ]
    return jsonify(data), 200

@app.route('/restaurant_pizzas', methods=['POST'])       
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    pizza = db.session.get(Pizza, pizza_id)
    restaurant = db.session.get(Restaurant, restaurant_id)

    # Match test expectations exactly
    if pizza is None or restaurant is None or price is None or not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400

    new_rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    db.session.add(new_rp)
    db.session.commit()

    response_data = {
        "id": new_rp.id,
        "price": new_rp.price,
        "pizza_id": pizza.id,
        "restaurant_id": restaurant.id,
        "pizza": {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        },
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        }
    }

    return jsonify(response_data), 201




if __name__ == "__main__":
    app.run(port=5555, debug=True)
