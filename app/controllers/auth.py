from flask import Blueprint, request, jsonify
from app.models import User, db
import jwt
from datetime import datetime, timedelta
import os

auth_bp = Blueprint("auth", __name__)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
ALGORITHM = "HS256"

def token_required(f):
    def decorator(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]  

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            decoded_token = jwt.decode(
                token, SECRET_KEY, algorithms=[ALGORITHM])
            current_user_id = decoded_token["sub"]  # Use the "sub" claim
            current_user_role = decoded_token["role"]
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(current_user_id, current_user_role, *args, **kwargs)

    return decorator


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401

    expiration = datetime.utcnow() + timedelta(hours=24)
    access_token = jwt.encode(
        {"sub": str(user.id), "role": str(user.role.value),
         "exp": expiration},  
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return jsonify({"access_token": access_token}), 200
