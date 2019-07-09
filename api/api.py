import os
import json
from bson import ObjectId
from flask_cors import CORS
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

app = Flask(__name__)

load_dotenv()
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['DB_URL'] = os.getenv('DB_URL')
CORS(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

mongoClient = MongoClient(app.config['DB_URL'])
db = mongoClient.flaskToDo

@app.route('/auth/signup', methods=['POST'])
def signup():
  req = request.json

  # Check if email and password are present in request
  email = req.get('email', None)
  password = req.get('password', None)

  if not email or not password:
    res = { 'message': 'Email or password missing.', 'errorCode': 1, 'user': None }
    return Response(json.dumps(res), status=400, mimetype='application/json')

  # Search in db for user
  existing_user = db.users.find_one({ 'email': email })

  if existing_user:
    res = { 'message': 'Could not create account for this email.', 'errorCode': 1, 'user': None }
    return Response(json.dumps(res), status=400, mimetype='application/json')

  user = {
    'email': email,
    'password': bcrypt.generate_password_hash(password).decode('utf-8')
  }
  result = db.users.insert_one(user)
  user['_id'] = str(user['_id'])

  res = { 'message': 'User created succesfully', 'errorCode': 0, 'user': user}
  return Response(json.dumps(res), status=200, mimetype='application/json')

@app.route('/auth/login', methods=['POST'])
def login():
  req = request.json

  # Check if email and password are present in request
  email = req.get('email', None)
  password = req.get('password', None)

  if not email or not password:
    res = { 'message': 'Email or password missing.', 'errorCode': 1, 'user': None, 'token': None}
    return Response(json.dumps(res), status=500, mimetype='application/json')

  # Search in db for user
  existing_user = db.users.find_one({ 'email': email })
  if not existing_user:
    res = { 'message': 'User not found.', 'errorCode': 1, 'user': None, 'token': None }
    return Response(json.dumps(res), status=404, mimetype='application/json')

  # Compare passwords
  if bcrypt.check_password_hash(existing_user.get('password'), password):
    user = {
      'email': existing_user.get('email'),
      'id': str(existing_user.get('_id'))
    }

    # Return data and token
    token = create_access_token(identity=user, expires_delta=timedelta(days=1))
    res = { 'message': 'User logged in succesfully', 'errorCode': 0, 'user': user, 'token': token}

    return Response(json.dumps(res), status=200, mimetype='application/json')

  else:
    res = { 'message': 'Incorrect email or password.', 'errorCode': 1, 'user': None, 'token': None }
    return Response(json.dumps(res), status=400, mimetype='application/json')

@app.route('/api/user/tasks', methods=['GET'])
@jwt_required
def get_tasks():
  current_user = get_jwt_identity()

  if current_user:
    tasks = list(db.tasks.find({ 'owner': current_user.get('id') }))
    for task in tasks:
        task['_id'] = str(task['_id'])

    res = { 'message': 'Tasks fetched successfully', 'errorCode': 0, 'tasks': tasks }

    return Response(json.dumps(res), status=200, mimetype='application/json')

  else:
    res = { 'message': 'Authorization failed.', 'errorCode': 1, 'tasks': None }
    return Response(json.dumps(res), status=403, mimetype='application/json')

@app.route('/api/tasks', methods=['POST'])
@jwt_required
def create_task():
  current_user = get_jwt_identity()

  if current_user:
    req = request.json

    task = {
      'owner': current_user.get('id'),
      'title': req.get('title'),
      'content': req.get('content'),
      'created_date': str(datetime.now()),
      'due_date': req.get('due_date')
    }

    result = db.tasks.insert_one(task)
    task['_id'] = str(task['_id'])

    res = { 'message': 'Task created succesfully', 'errorCode': 0, 'task': task}
    return Response(json.dumps(res), status=200, mimetype='application/json')

  else:
    res = { 'message': 'Authorization failed.', 'errorCode': 1, 'task': None }
    return Response(json.dumps(res), status=403, mimetype='application/json')

@app.route('/api/tasks/<taskId>', methods=['GET'])
@jwt_required
def get_task(taskId):
  current_user = get_jwt_identity()

  if current_user:
    task = db.tasks.find_one({'_id': ObjectId(taskId), 'owner': current_user.get('id')})

    if task:
      task['_id'] = str(task['_id'])

      res = { 'message': 'Task fetched successfully', 'errorCode': 0, 'task': task }
      return Response(json.dumps(res), status=200, mimetype='application/json')

    res = { 'message': 'Task not found.', 'errorCode': 1, 'task': None }
    return Response(json.dumps(res), status=404, mimetype='application/json')

  else:
    res = { 'message': 'Authorization failed.', 'errorCode': 1, 'task': None }
    return Response(json.dumps(res), status=403, mimetype='application/json')

@app.route('/api/tasks/<taskId>', methods=['PUT'])
@jwt_required
def edit_task(taskId):
  current_user = get_jwt_identity()

  if current_user:
    req = request.json

    newTask = {
      'owner': current_user.get('id'),
      'title': req.get('title'),
      'content': req.get('content'),
      'created_date': req.get('created_date'),
      'due_date': req.get('due_date')
    }
    result = db.tasks.find_one_and_replace({'_id': ObjectId(taskId), 'owner': current_user.get('id')}, newTask)

    if result:
      res = { 'message': 'Task updated successfully.', 'errorCode': 0, 'task': newTask }
      return Response(json.dumps(res), status=200, mimetype='application/json')

    res = { 'message': 'Task not found.', 'errorCode': 1, 'task': None }
    return Response(json.dumps(res), status=404, mimetype='application/json')

  else:
    res = { 'message': 'Authorization failed.', 'errorCode': 1, 'task': None }
    return Response(json.dumps(res), status=403, mimetype='application/json')

@app.route('/api/tasks/<taskId>', methods=['DELETE'])
@jwt_required
def delete_task(taskId):
  current_user = get_jwt_identity()

  if current_user:
    result = db.tasks.delete_one({ '_id': ObjectId(taskId), 'owner': current_user.get('id')})

    if result:
      res = { 'message': 'Task deleted successfully.', 'errorCode': 0 }
      return Response(json.dumps(res), status=200, mimetype='application/json')

    res = { 'message': 'Could not delete task.', 'errorCode': 1 }
    return Response(json.dumps(res), status=500, mimetype='application/json')

  else:
    res = { 'message': 'Authorization failed.', 'errorCode': 1 }
    return Response(json.dumps(res), status=403, mimetype='application/json')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)
