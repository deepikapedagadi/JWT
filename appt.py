from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = "DEEPS"   # secret for JWT
app.config['REFRESH_SECRET'] = "KP"  # secret for refresh tokens


# Decorator to check access token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("x-access-token")
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except Exception as e:
            return jsonify({"message": "Token invalid", "error": str(e)}), 401
        return f(*args, **kwargs)
    return decorated


# Login Route
@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if auth and auth.username == "admin@23" and auth.password == "password":
        access_token = jwt.encode(
            {
                'user': auth.username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1)  # 1 min expiry
            },
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        refresh_token = jwt.encode(
            {
                'user': auth.username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # valid for 1 hour
            },
            app.config['REFRESH_SECRET'],
            algorithm="HS256"
        )
        return jsonify({"access_token": access_token, "refresh_token": refresh_token})

    return jsonify({"message": "Invalid credentials"}), 401


# Refresh Route
@app.route('/refresh', methods=['POST'])
def refresh():
    token = request.headers.get("x-refresh-token")
    if not token:
        return jsonify({"message": "Refresh token is missing"}), 401
    try:
        data = jwt.decode(token, app.config['REFRESH_SECRET'], algorithms=["HS256"])
        new_access_token = jwt.encode(
            {
                'user': data['user'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
            },
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({"access_token": new_access_token})
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Refresh token expired, login again"}), 401
    except Exception as e:
        return jsonify({"message": "Invalid refresh token", "error": str(e)}), 401


# Protected Route
@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({"message": "You have accessed a protected route"})


if __name__ == '__main__':
    app.run(debug=True)