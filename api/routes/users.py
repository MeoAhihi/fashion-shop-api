from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash

from ..utils.jwt_utils import require_bearer_token


users_bp = Blueprint("users", __name__, url_prefix="/api/users")


def _serialize_user(doc: dict) -> dict:
    return {
        "id": str(doc.get("_id")),
        "fullname": doc.get("fullname"),
        "email": doc.get("email"),
        "createdAt": doc.get("createdAt"),
        "updatedAt": doc.get("updatedAt"),
    }


@users_bp.get("")
def list_users():
    if not require_bearer_token():
        return jsonify({"error": "Unauthorized"}), 401
    users = current_app.config["USERS_COLLECTION"]
    docs = list(users.find())
    return jsonify({"users": [_serialize_user(d) for d in docs]})


@users_bp.get("/<user_id>")
def get_user(user_id: str):
    if not require_bearer_token():
        return jsonify({"error": "Unauthorized"}), 401
    users = current_app.config["USERS_COLLECTION"]
    try:
        oid = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Invalid user id"}), 400
    doc = users.find_one({"_id": oid})
    if not doc:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"user": _serialize_user(doc)})


@users_bp.post("")
def create_user():
    # if not require_bearer_token():
    #     return jsonify({"error": "Unauthorized"}), 401
    users = current_app.config["USERS_COLLECTION"]
    body = request.get_json(silent=True) or {}
    fullname = (body.get("fullname") or "").strip()
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not fullname or not email or not password:
        return jsonify({"error": "fullname, email, and password are required"}), 400
    if users.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 409
    now_iso = datetime.now(timezone.utc).isoformat()
    doc = {
        "fullname": fullname,
        "email": email,
        "passwordHash": generate_password_hash(password),
        "createdAt": now_iso,
        "updatedAt": now_iso,
    }
    result = users.insert_one(doc)
    created = users.find_one({"_id": result.inserted_id})
    return jsonify({"user": _serialize_user(created)}), 201


@users_bp.put("/<user_id>")
def update_user(user_id: str):
    if not require_bearer_token():
        return jsonify({"error": "Unauthorized"}), 401
    users = current_app.config["USERS_COLLECTION"]
    try:
        oid = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Invalid user id"}), 400
    body = request.get_json(silent=True) or {}
    update: dict = {}
    if "fullname" in body:
        fullname = (body.get("fullname") or "").strip()
        if not fullname:
            return jsonify({"error": "fullname cannot be empty"}), 400
        update["fullname"] = fullname
    if "email" in body:
        email = (body.get("email") or "").strip().lower()
        if not email:
            return jsonify({"error": "email cannot be empty"}), 400
        existing = users.find_one({"email": email, "_id": {"$ne": oid}})
        if existing:
            return jsonify({"error": "Email already in use"}), 409
        update["email"] = email
    if "password" in body:
        password = body.get("password") or ""
        if not password:
            return jsonify({"error": "password cannot be empty"}), 400
        update["passwordHash"] = generate_password_hash(password)
    if not update:
        return jsonify({"error": "No fields to update"}), 400
    update["updatedAt"] = datetime.now(timezone.utc).isoformat()
    result = users.find_one_and_update(
        {"_id": oid},
        {"$set": update},
        return_document=True,
    )
    if not result:
        return jsonify({"error": "Not found"}), 404
    updated = users.find_one({"_id": oid})
    return jsonify({"user": _serialize_user(updated)})


@users_bp.delete("/<user_id>")
def delete_user(user_id: str):
    if not require_bearer_token():
        return jsonify({"error": "Unauthorized"}), 401
    users = current_app.config["USERS_COLLECTION"]
    try:
        oid = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Invalid user id"}), 400
    result = users.delete_one({"_id": oid})
    if result.deleted_count == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"deleted": True})


