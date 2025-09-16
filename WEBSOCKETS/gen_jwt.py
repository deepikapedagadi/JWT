# generate_jwt.py
import jwt
import datetime

SECRET_KEY = "mysecret"  # same key must be on server

def create_token(username):
    payload = {
        "user": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)  # 5 min expiry
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

if __name__ == "__main__":
    token = create_token("deepika")
    print("Your JWT token:\n", token)
