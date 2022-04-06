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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
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

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
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

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    data = request.json
    recipe = data["recipe"]
    # TODO add handling of malformed requests (missing data) and other errors
    drink = Drink(
        title=data["title"],
        recipe= json.dumps([
            {"name": ingredient["name"],
            "color": ingredient["color"],
            "parts": ingredient["parts"]} for ingredient in recipe])
    )
    drink.insert()
    res = {"success": True, "drinks": [drink.long()]}
    # TODO Add test to res
    return jsonify(res)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    # TODO add handling of malformed requests and other errors
    drink = Drink.query.get(drink_id)
    data = request.json
    recipe = data.get("recipe")
    if recipe:
        drink.recipe= json.dumps([
            {"name": ingredient["name"],
            "color": ingredient["color"],
            "parts": ingredient["parts"]} for ingredient in recipe])
    title = data.get("title")
    if title:
        drink.title = data["title"]
    drink.update()
    res = {"success": True, "drinks": [drink.long()]}
    return jsonify(res)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<drink_id>', methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    #TODO add error handling
    drink.delete()
    res = {"success": True, "delete": drink_id}
    return jsonify(res)
# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422



@app.errorhandler(AuthError)
def not_permitted(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error["description"]
    }), 403


@app.errorhandler(404)
def not_permitted(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404
