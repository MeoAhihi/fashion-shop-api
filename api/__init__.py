import os
from datetime import datetime, timezone

from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI is not set. Define it in your .env file.")

    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change-me-in-.env")
    app.config["JWT_TTL_MINUTES"] = int(os.getenv("JWT_TTL_MINUTES", "60"))

    mongo_client = MongoClient(mongo_uri)
    db = mongo_client[os.getenv("MONGO_DB", "fashion_shop")]
    app.config["DB"] = db
    app.config["USERS_COLLECTION"] = db["users"]

    @app.get("/")
    def index():
        return jsonify({"status": "ok", "time": datetime.now(timezone.utc).isoformat()})

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    return app


