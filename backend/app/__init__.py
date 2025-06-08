from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client["SkillSyncCluster"]

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    JWTManager(app)

    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.projects import project_bp
    from app.routes.skill import skills_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.resume_upload import resume_bp
    from app.routes.admin_dashboard import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(project_bp, url_prefix='/api')
    app.register_blueprint(skills_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(resume_bp, url_prefix='/api/resume')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app