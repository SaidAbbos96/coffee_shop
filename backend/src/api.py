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


# --------------------------------------------
# Good day. Sorry if something went wrong and
# everyone wrote a message written with a translator.

# All codes are formatted by the method.
# autopep8 your_script.py    / dry-run, only print
# autopep8 -i your_script.py / replace content
# and using an online reformer
# http://pep8online.com/

# --------------------------------------------

# basic route
@app.route("/")
def home():
    hiText = "Hi ! I`m SaidAbbos.<br> abbos.xudoyqulov@gmail.com"
    return str(hiText)
# '''
# @TODO uncomment the following line to initialize the datbase
# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
# '''
# db_drop_and_create_all()

# ROUTES
# '''
# @TODO implement endpoint
#     GET /drinks
#         it should be a public endpoint
#         it should contain only the drink.short() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks}
# where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''
# Drinks list controller.


@app.route('/drinks')
def get_drinks_db():
    # We get a list of all the drinks from the database.
    drinks = Drink.query.all()

    # If there is no drink return an error.
    if len(drinks) == 0:
        abort(404, "error. not a single drink found")

    # Returns a list of the drink in the appropriate format and a result code.
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200

# '''
# @TODO implement endpoint
#     GET /drinks-detail
#         it should require the 'get:drinks-detail' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drinks}
# where drinks is the list of drinks
#         or appropriate status code indicating reason for failure
# '''
#  A checklist for bartenders if the bartender ask
# returns the recipe for a drink.


@app.route('/drinks-detail')
# Check here the rights of bartenders.
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    # get all drinks and format using .long()
    drinks = Drink.query.all()

    # 404 if no drinks found
    if len(drinks) == 0:
        abort(404)

    # format using .long()
    drinks_long = [drink.long() for drink in drinks]
    Fout = open("log.txt", "w")
    Fout.write(str(drinks_long))
    Fout.close()
    # return drinks
    return jsonify({
        'success': True,
        'drinks': drinks_long
    }), 200


# '''
# @TODO implement endpoint
#     POST /drinks
#         it should create a new row in the drinks table
#         it should require the 'post:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink}
# where drink an array containing only the newly created drink
#         or appropriate status code indicating reason for failure
# '''
# Making a new drink.
@app.route('/drinks', methods=['POST'])
# Manager permission check
@requires_auth('post:drinks')
def add_drink(jwt):
    try:
        # get information from json
        body = request.get_json()
        title = body['title']
        recipe = body['recipe']

        # create a new drink
        drink = Drink(title=title, recipe=json.dumps(recipe))
        # Save the drink to the database.
        drink.insert()
    except:
        abort(422, "error. Failed to save drink to database.")
    # If all OK returned the drink.
    return jsonify({
        "success": True,
        "drinks": drink.long()
    }), 200


# '''
# @TODO implement endpoint
#     PATCH /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should update the corresponding row for <id>
#         it should require the 'patch:drinks' permission
#         it should contain the drink.long() data representation
#     returns status code 200 and json {"success": True, "drinks": drink}
# where drink an array containing only the updated drink
#         or appropriate status code indicating reason for failure
# '''
# Updating the recipe for a drink.
@app.route('/drinks/<int:id>', methods=['PATCH'])
# We check the permission for this operation.
@requires_auth('patch:drinks')
def edit_drink_by_id(*args, **kwargs):
    try:
        # get an electrifier drink from get link
        id = kwargs['id']
        # We are looking for this drink by identifier.
        drink = Drink.query.filter_by(id=id).one_or_none()

        # If the drink is not found, return errors.
        if drink is None:
            abort(404, 'Error. drink with which identifier is not found.')

        # get information from json
        body = request.get_json()

        # If the name of the drink is changed, then we change the database.
        if 'title' in body:
            drink.title = body['title']

        # If the recipe of the drink is changed, then we change the database.
        if 'recipe' in body:
            drink.recipe = json.dumps(body['recipe'])

        # update drink in database
        drink.insert()
    except:
        # In case of an error, we return a message error code.
        abort(400, 'Error. Failed to update the drink.')

    # Return updated drink information.
    return jsonify({
        'success': True,
        'drinks': drink.long()
    }), 200

# '''
# @TODO implement endpoint
#     DELETE /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should delete the corresponding row for <id>
#         it should require the 'delete:drinks' permission
#     returns status code 200 and json {"success": True, "delete": id}
#      where id is the id of the deleted record
#         or appropriate status code indicating reason for failure
# '''
# Controller removing a specific drink.


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(*args, **kwargs):
    try:
        # get an electrifier drink from get link
        id = kwargs['id']
        # We are looking for this drink by identifier.
        drink = Drink.query.filter_by(id=id).one_or_none()
        # In case of an error, we return a message error code.
        if drink is None:
            abort(404, 'An error occurred while uninstalling.')

        # I delete the drink from the database.
        drink.delete()
    except:
        # In case of an error, we return a message error code.
        abort(404, 'An error occurred while uninstalling.')

    # We return the status of the request and the
    # identifier of the remote drink.
    return jsonify({
        'success': True,
        'delete': id
    }), 200


# Error Handling
# '''
# Error handling for unprocessable entity
# '''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


# '''
# @TODO implement error handlers using the @app.errorhandler(error) decorator
#     each error handler should return (with approprate messages):
#              jsonify({
#                     "success": False,
#                     "error": 404,
#                     "message": "resource not found"
#                     }), 404
# '''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


# Error response to the wrong request.
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Sorry for the request is incorrect"
    }), 400


# '''
# @TODO implement error handler for AuthError
#     error handler should conform to general task above
# '''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
