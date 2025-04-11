from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db
from models.user import insert_users
from models.department import insert_departments
from models.complaint import Complaint
from resources.auth import api as auth_ns
from resources.complaint import api as complaint_ns
from extensions import blacklist  # Import blacklist
from flask_cors import CORS

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
    app.config.from_object(config_class)

    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    cors = CORS(app, origins="*", send_wildcard=True)
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

    with app.app_context():
        db.create_all()
        # insert_departments()
        # insert_users()
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
