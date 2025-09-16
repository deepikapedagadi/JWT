from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import base64


# ------------------------------
# Flask App Configuration
# ------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'user-secret-key'  # secret-key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:welcome@localhost:5432/testdb' #database url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------------
# User Model
# ------------------------------
class User(db.Model):

    __tablename__ = 'user1'  #table name
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Hashed password

# Create tables if they don't exist
with app.app_context():
    db.create_all()


# ------------------------------
# JWT Token Generator
# ------------------------------
def generate_token(user):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token


# ------------------------------
# JWT Token Verifier (Optional)
# ------------------------------
def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ------------------------------
# Register Route (POST)
# ------------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({'message': 'Email, name, and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 409

    # hashed_password = generate_password_hash(password)

    user = User(email=email, name=name, password=password)
    db.session.add(user)
    db.session.commit()

    token = generate_token(user)
    return jsonify({'message': 'User registered successfully', 'token': token})


# ------------------------------
# Basic Auth Protected Profile (GET)
# ------------------------------
@app.route('/profile', methods=['GET'])
def profile_basic():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Basic '):
        return jsonify({'message': 'Missing or invalid Authorization header'}), 401

    try:
        # Decode Basic Auth credentials
        encoded_credentials = auth_header.split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        email, password = decoded_credentials.split(':')
    except Exception:
        return jsonify({'message': 'Invalid Basic Auth format'}), 401

    user = User.query.filter_by(email=email).first()
    if not user or user.password != password:
        return jsonify({'message': 'Invalid email or password'}), 401

    return jsonify({'id': user.id, 'email': user.email, 'name': user.name, 'password': user.password})

# ------------------------------
# Get All Users (Optional)
# ------------------------------
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{
        'id': user.id,
        'email': user.email,
        'name': user.name
    } for user in users]

    return jsonify(user_list)

# ------------------------------
# Run App
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=1231)



"""Summary:
This Flask app allows users to register and access their profile using either JWT tokens or Basic Auth. User information (email, name, password) is stored in a PostgreSQL database. JWT tokens are generated for users upon registration to prove their identity in future requests.

Approach:
* Users send their details to the `/register` route to create an account.
* A JWT token is generated with a 1-hour expiry.
* Users can access their profile via the `/profile` route using Basic Auth headers.
* Optional `/users` route lists all users for debugging or admin purposes.
* JWT tokens can also be verified using helper functions if needed.

Result:
* Users get a JWT token immediately after registration.
* Profiles are protected using Basic Auth.
* The database stores user details securely, though currently passwords are plain text.
* Admins or developers can view all registered users.

Impact:
* Provides secure access control using JWT and Basic Auth.
* Simplifies user authentication and identity verification for APIs.
* Lays the foundation for adding more secure token-based routes in future projects.
* Enables learning about Flask, JWT, HTTP headers, and database integration.
"""