from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
import logging

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key_here')

users = {
    "user1": generate_password_hash("password1"),
    "user2": generate_password_hash("password2")
}

permissions = {
    "user1": ["view", "edit"],
    "user2": ["view", "edit"]
}

fitness_data = {}

logging.basicConfig(level=logging.INFO)

def log_action(action):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logging.info('Action: {}'.format(action))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            logging.warning("A valid token is missing for action")
            return jsonify({'message': 'A valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['public_id']
            logging.info(f"User {current_user} accessed with token.")
        except:
            logging.error("Token is invalid")
            return jsonify({'message': 'Token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorated

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(current_user, *args, **kwargs):
            if permission not in permissions.get(current_user, []):
                logging.warning(f"User {current_user} access denied for permission: {permission}")
                return jsonify({'message': 'Permission denied'})
            logging.info(f"User {current_user} granted permission: {permission}")
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

@app.route('/register', methods=['POST'])
@log_action('User Registration Attempt')
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username in users:
        return jsonify({'message': 'User already exists'}), 409
    users[username] = generate_password_hash(password)
    permissions[username] = ["view", "edit"]
    return jsonify({'message': 'Registered successfully'}), 201

@app.route('/login', methods=['GET', 'POST'])
@log_action('User Login Attempt')
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        logging.warning("Login verification failed due to missing or incorrect credentials.")
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if auth.username in users and check_password_hash(users[auth.username], auth.password):
        token = jwt.encode({'public_id': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
        logging.info(f"{auth.username} logged in successfully.")
        return jsonify({'token': token})

    logging.warning(f"Could not verify user: {auth.username}")
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/fitness_data', methods=['POST'])
@token_required
@log_action('Post Fitness Data')
def post_fitness_data(current_user):
    data = request.get_json()
    date = data.get('date')
    exercises = data.get('exercises')
    duration = data.get('duration')
    if not date or not exercises or not duration:
        return jsonify({'message': 'Data is missing'}), 400
    fitness_data[current_user] = fitness_data.get(current_user, []) + [{
        'date': date,
        'exercises': exercises,
        'duration': duration
    }]
    return jsonify({'message': 'Fitness data added successfully'}), 201

@app.route('/fitness_data', methods=['GET'])
@token_required
@log_action('Get Fitness Data')
def get_fitness_data(current_user):
    data = fitness_data.get(current_user, [])
    return jsonify(data), 200

@app.route('/update_fitness_data', methods=['PUT'])
@token_required
@require_permission('edit')
@log_action('Update Fitness Data')
def update_fitness_data(current_user):
    data = request.get_json()
    date = data.get('date')
    found = False
    for record in fitness_data.get(current_user, []):
        if record['date'] == date:
            record.update(data)
            found = True
            break
    if not found:
        return jsonify({'message': 'Record not found'}), 404
    return jsonify({'message': 'Fitness data updated successfully'}), 200

@app.route('/delete_fitness_data', methods=['DELETE'])
@token_required
@require_permission('edit')
@log_action('Delete Fitness Data')
def delete_fitness_data(current_user):
    data = request.get_json()
    date = data.get('date')
    original_size = len(fitness_data.get(current_user, []))
    fitness_data[current_user] = [record for record in fitness_data.get(current_user, []) if record['date'] != date]
    if len(fitness_data[current_user]) == original_size:
        return jsonify({'message': 'Record not found'}), 404
    return jsonify({'message': 'Fitness data deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)