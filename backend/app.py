from flask import Flask
from flask_compress import Compress
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db
from models.user import insert_users
from models.department import insert_departments
from resources.auth_views import auth_ns
from resources.complaint_views import complaint_ns
from resources.analytics_views import analytics_ns
from extensions import blacklist  # Import blacklist

# Define authorizations for Swagger UI
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter the JWT token in the format: Bearer <token>'
    }
}

def create_app(config_class=Config):
    app = Flask(__name__)
    Compress(app)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    # Token blacklist setup
    blacklist = set()

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in blacklist

    # Initialize Api with authorizations
    api = Api(
        app,
        title='Complaint Management API',
        version='1.0',
        authorizations=authorizations,  # Add authorizations here
        security='Bearer Auth'  # Enable Bearer Auth by default
    )
    api.add_namespace(auth_ns)
    api.add_namespace(complaint_ns)
    api.add_namespace(analytics_ns)

    with app.app_context():
        db.create_all()
        #insert_departments()
        #insert_users()
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)