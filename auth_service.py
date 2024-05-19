from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key_here')

users = {
    "user1": generate_password_hash("password1"),
    "user2": generate_password_hash("password2")
}

permissions = {
    "user1": ["view"],
    "user2": ["view", "edit"]
}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'A valid token is missing'})

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['public_id']
        except:
            return jsonify({'message': 'Token is invalid'})

        return f(current_user, *args, **kwargs)
    
    return decorated

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(current_user, *args, **kwargs):
            if permission not in permissions.get(current_user, []):
                return jsonify({'message': 'Permission denied'})
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if auth.username in users and check_password_hash(users[auth.username], auth.password):
        token = jwt.encode({'public_id': auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token' : token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/user', methods=['GET'])
@token_required
def get_user(current_user):
    return jsonify({'user': current_user})

@app.route('/edit', methods=['GET'])
@require_permission('edit')
def edit_resource(current_user):
    return jsonify({'message': f'{current_user} edited the resource'})

if __name__ == '__main__':
    app.run(debug=True)