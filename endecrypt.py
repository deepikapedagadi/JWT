from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import base64
import os
import json
from cryptography.fernet import Fernet

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'user-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:welcome@localhost:5432/testdb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ENCRYPTION_KEY: keep this safe in env for real use.
enc_key = os.environ.get('ENCRYPTION_KEY')
if not enc_key:
    # WARNING: If you don't set ENCRYPTION_KEY env var, a new ephemeral key is generated
    # and encrypted data will not be decryptable after restart. For demo only.
    enc_key = Fernet.generate_key().decode()
    print("WARNING: No ENCRYPTION_KEY set — generated ephemeral key (won't persist across restarts).")
app.config['ENCRYPTION_KEY'] = enc_key.encode()

# ADMIN_KEY for decrypt endpoint protection (change in env in real setups)
app.config['ADMIN_KEY'] = os.environ.get('ADMIN_KEY', 'admin-demo-key')

db = SQLAlchemy(app)

# ------------------------------
# User Model
# ------------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)        # hashed (for auth)
    password_encrypted = db.Column(db.Text, nullable=True)     # reversible encrypted (demo only)

with app.app_context():
    db.create_all()

# ------------------------------
# Token generation
# ------------------------------
def generate_token(user, hours=1):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

# ------------------------------
# Helpers for Fernet
# ------------------------------
def get_cipher():
    return Fernet(app.config['ENCRYPTION_KEY'])

def encrypt_password(plain_password: str) -> str:
    cipher = get_cipher()
    token = cipher.encrypt(plain_password.encode())
    return token.decode('utf-8')  # store as str

def decrypt_password(encrypted_str: str) -> str:
    cipher = get_cipher()
    plain = cipher.decrypt(encrypted_str.encode())
    return plain.decode('utf-8')

# ------------------------------
# Routes
# ------------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    if not email or not name or not password:
        return jsonify({'status': 'error', 'message': 'Email, name and password are required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'status': 'error', 'message': 'User already exists'}), 409

    hashed = generate_password_hash(password)
    encrypted = encrypt_password(password)  # demo reversible storage
    user = User(email=email, name=name, password=hashed, password_encrypted=encrypted)
    db.session.add(user)
    db.session.commit()
    token = generate_token(user)
    return jsonify({'status': 'success', 'message': 'User registered successfully', 'token': token})

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    token = generate_token(user)
    return jsonify({'status': 'success', 'message': 'Login successful', 'token': token})

# Admin-only: decrypt a user's encrypted password (DEMO ONLY)
@app.route('/admin/decrypt', methods=['POST'])
def admin_decrypt():
    admin_key = request.headers.get('X-ADMIN-KEY', '')
    if admin_key != app.config['ADMIN_KEY']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json or {}
    email = data.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'email is required in body'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    if not user.password_encrypted:
        return jsonify({'status': 'error', 'message': 'No encrypted password stored for this user'}), 404

    try:
        plain = decrypt_password(user.password_encrypted)
        # WARNING: returning the plain password is unsafe — demo only
        return jsonify({'status': 'success', 'email': user.email, 'decrypted_password': plain})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Decryption failed', 'error': str(e)}), 500

# Admin-only: manually encrypt a supplied password for an existing user
@app.route('/admin/encrypt-user', methods=['POST'])
def admin_encrypt_user():
    admin_key = request.headers.get('X-ADMIN-KEY', '')
    if admin_key != app.config['ADMIN_KEY']:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'status': 'error', 'message': 'email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    user.password_encrypted = encrypt_password(password)
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Encrypted password stored for {email}'})

# Existing verify/decode endpoints (unchanged)
@app.route('/decode', methods=['GET', 'POST'])
def decode_route():
    token = _extract_token_from_request(request)
    if not token:
        return jsonify({'status': 'error', 'message': 'No token provided. Use Authorization: Bearer <token>, JSON {"token":...} or ?token=...'}), 400
    try:
        header, payload, signature_b64 = decode_jwt_unverified(token)
        return jsonify({'verified': False, 'header': header, 'payload': payload, 'signature_b64url': signature_b64})
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to decode token', 'error': str(e)}), 400

@app.route('/verify', methods=['GET', 'POST'])
def verify_route():
    token = _extract_token_from_request(request)
    if not token:
        return jsonify({'status': 'error', 'message': 'No token provided.'}), 400
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        header = jwt.get_unverified_header(token)
        return jsonify({'verified': True, 'header': header, 'payload': payload})
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'error', 'message': 'Token expired'}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({'status': 'error', 'message': 'Invalid token', 'error': str(e)}), 401

# Helpers reused from your code
def _b64url_decode(data: str) -> bytes:
    if isinstance(data, str):
        data = data.encode('utf-8')
    rem = len(data) % 4
    if rem:
        data += b'=' * (4 - rem)
    return base64.urlsafe_b64decode(data)

def decode_jwt_unverified(token: str):
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError('Token must have exactly 3 parts separated by dots.')
    h_b64, p_b64, s_b64 = parts
    header = json.loads(_b64url_decode(h_b64))
    payload = json.loads(_b64url_decode(p_b64))
    return header, payload, s_b64

def _extract_token_from_request(req):
    auth = req.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth.split(' ', 1)[1].strip()
    if req.is_json:
        t = req.json.get('token')
        if t:
            return t.strip()
    t = req.args.get('token')
    if t:
        return t.strip()
    return None

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    # Return only safe info here
    return jsonify([{'id': u.id, 'email': u.email, 'name': u.name} for u in users])

if __name__ == '__main__':
    app.run(debug=True, port=4567)


with app.app_context():
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(rule)

#from your_app_file import db # pyright: ignore[reportMissingImports]
#db.drop_all()
#db.create_all()


from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())

