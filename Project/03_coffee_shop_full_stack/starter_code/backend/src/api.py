import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

    
'''
Uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=["GET"])
def get_drinks():
    drinks = Drink.query.all()
    if drinks:
        res =  {
            "success": True,
            "drinks": [d.short() for d in drinks]}
        return jsonify(res)
    else:
        abort(404)

@app.route('/drinks-detail', methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    drinks = Drink.query.all()
    if drinks:
        res =  {
            "success": True,
            "drinks": [d.long() for d in drinks]}
        return jsonify(res)
    else:
        abort(404)    


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    data = request.json
    if "recipe" not in data or "title" not in data:
        abort(400)
    try:
        recipe = json.dumps([
            {"name": ingredient["name"],
            "color": ingredient["color"],
            "parts": ingredient["parts"]} for ingredient in data["recipe"]])
    except KeyError:
        abort(400)
    drink = Drink(
        title=data["title"],
        recipe=recipe
    )
    drink.insert()
    res = {"success": True, "drinks": [drink.long()]}
    return jsonify(res)

@app.route('/drinks/<drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    # TODO add handling of malformed requests and other errors
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    data = request.json
    request_recipe = data.get("recipe")

    if request_recipe:
        try:
            recipe = json.dumps([
                {"name": ingredient["name"],
                "color": ingredient["color"],
                "parts": ingredient["parts"]} for ingredient in request_recipe])
        except KeyError:
            abort(400)
        drink.recipe=recipe
    title = data.get("title")
    if title:
        drink.title = title
    drink.update()
    res = {"success": True, "drinks": [drink.long()]}
    return jsonify(res)

@app.route('/drinks/<drink_id>', methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if drink:
        drink.delete()
        res = {"success": True, "delete": drink_id}
        return jsonify(res)
    else:
        abort(404)

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error["description"]
    }), error.status_code

@app.errorhandler(404)
def not_permitted(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404

@app.errorhandler(400)
def malformed(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Malformed request"
    }), 400
