import os
from flask import Flask, render_template, send_from_directory
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db
from models.user import insert_users
from models.department import insert_departments
from models.complaint import Complaint
from extensions import blacklist  # Import blacklist
from flask_cors import CORS
# from resources.auth_views import auth_ns
from resources.complaint_views import complaint_ns
from resources.auth_views import auth_ns
from resources.analytics_views import analytics_ns
from models.user import User
from models.sub_category import SubCategory
from scripts.seed_data import generate_fake_data
# Define authorizations for Swagger UI
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter the JWT token in the format: Bearer <token>'
    }
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    cors = CORS(app, origins="*", send_wildcard=True)
    # Token blacklist setup
    blacklist = set()

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in blacklist

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    @app.route('/')
    @app.route('/<path:path>')
    def serve_react_app(path=""):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    # Initialize Api with authorizations
    api = Api(
        app,
        title='Complaint Management API',
        version='1.0',
        authorizations=authorizations,  # Add authorizations here
        security='Bearer Auth',
        doc="/doc"  # Enable Bearer Auth by default
    )
    api.add_namespace(auth_ns)
    api.add_namespace(complaint_ns)
    api.add_namespace(analytics_ns)
    with app.app_context():
        db.create_all()
        insert_departments()
        SubCategory.add_sub_category()
        # print(generate_fake_data(15, 4))  # Added print to see the result
        # insert_users()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
