from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

from ..utils.jwt_utils import issue_jwt


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _serialize_user(doc: dict) -> dict:
    return {
        "id": str(doc.get("_id")),
        "fullname": doc.get("fullname"),
        "email": doc.get("email"),
        "createdAt": doc.get("createdAt"),
        "updatedAt": doc.get("updatedAt"),
    }


@auth_bp.post("/register")
def register():
    users = current_app.config["USERS_COLLECTION"]
    body = request.get_json(silent=True) or {}
    fullname = (body.get("fullname") or "").strip()
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""

    if not fullname or not email or not password:
        return jsonify({"error": "fullname, email, and password are required"}), 400

    if users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    now_iso = datetime.now(timezone.utc).isoformat()
    user_doc = {
        "fullname": fullname,
        "email": email,
        "passwordHash": generate_password_hash(password),
        "createdAt": now_iso,
        "updatedAt": now_iso,
    }
    inserted = users.insert_one(user_doc)
    created = users.find_one({"_id": inserted.inserted_id})
    token = issue_jwt(str(created["_id"]), created["email"])
    return jsonify({"user": _serialize_user(created), "token": token}), 201


@auth_bp.post("/login")
def login():
    users = current_app.config["USERS_COLLECTION"]
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = users.find_one({"email": email})
    if not user or not check_password_hash(user.get("passwordHash", ""), password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = issue_jwt(str(user["_id"]), user["email"])
    return jsonify({"user": _serialize_user(user), "token": token})


