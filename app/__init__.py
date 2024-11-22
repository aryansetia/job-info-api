from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Load configurations from environment variables
    app.config.from_object("config.Config")

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Register Blueprints for different routes
    from app.controllers.candidate import candidate_bp
    from app.controllers.auth import auth_bp
    from app.controllers.recruiter import recruiter_bp

    # Registering Blueprints with url_prefixes
    app.register_blueprint(candidate_bp, url_prefix="/candidate")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(recruiter_bp, url_prefix="/recruiter")


    return app
