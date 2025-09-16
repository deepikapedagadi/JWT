from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)

# Secret for signing JWTs
SECRET_KEY = "super-secret-key"  # use env variable in production
ALGORITHM = "HS256"


# Demo user store
users = {
    "deeps": generate_password_hash("password345"),
    "bob": generate_password_hash("bobspassword"),
}

def create_jwt(username):
    """Generate a JWT for the given username"""
    payload = {
        "sub": username,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=15),  # expires in 5 minutes
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    if isinstance(token, bytes):  # handle old PyJWT versions
        token = token.decode("utf-8")
    return token

def decode_jwt(token):
    """Decode and verify JWT"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def authenticate():
    """Send a 401 requiring Basic Auth"""
    return make_response(
        "Could not verify your login!\n",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )

def check_basic_and_issue_token():
    """Check Basic Auth credentials, return JWT if valid"""
    auth = request.authorization
    if not auth or auth.username not in users:
        return None
    if not check_password_hash(users[auth.username], auth.password):
        return None
    return create_jwt(auth.username)

@app.route("/")
def index():
    return "Server running. Use /token or /secure"

@app.route("/token")
def token_endpoint():
    """Client calls with Basic Auth → returns JWT"""
    token = check_basic_and_issue_token()
    if not token:
        return authenticate()
    return jsonify({"jwt_token": token})

@app.route("/secure")
def secure():
    """
    Client still calls with Basic Auth.
    Server validates username/password,
    generates a JWT internally and decodes it before responding.
    """
    token = check_basic_and_issue_token()
    if not token:
        return authenticate()

    try:
        payload = decode_jwt(token)
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

    return jsonify({
        "message": f"Hello {payload['sub']}! You are authorized.",
        "jwt_payload": payload
    })

if __name__ == "__main__":
    app.run(debug=True)
