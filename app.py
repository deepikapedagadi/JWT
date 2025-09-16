from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# In-memory user store (username -> hashed password)
users = {
    "alice": generate_password_hash("password123"),
    "bob": generate_password_hash("bobspassword"),
}

def check_auth(username, password):
    """Check username/password against our store"""
    if username not in users:
        return False
    return check_password_hash(users[username], password)

def authenticate():
    """Send a 401 response that enables basic auth"""
    return make_response(
        "Could not verify your login!\n", 
        401, 
        {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )

@app.route("/")
def index():
    return "Server running. Try /protected"

@app.route("/protected")
def protected():
    # Get Basic Auth credentials from request
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    return jsonify({
        "message": f"Welcome, {auth.username}! You accessed a protected route."
    })

if __name__ == "__main__":
    app.run(debug=True)
