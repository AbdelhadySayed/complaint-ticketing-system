from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models.user import User
from models import db
from extensions import blacklist  # Import blacklist

api = Namespace('auth', description='Authentication operations')

login_model = api.model('Login', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})


register_model = api.model('Register', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@api.route('/login')
class UserLogin(Resource):
    @api.expect(login_model)
    def post(self):
        data = api.payload
        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return {
                'access_token': access_token,
                'message': 'Copy the access_token and use it in the Authorization header'
            }, 200
        return {'message': 'Invalid credentials'}, 401
        

@api.route('/admin_login')
class AdminLogin(Resource):
    @api.expect(login_model)
    def post(self):
        data = api.payload
        user = User.query.filter_by(username=data['username'], role="admin").first()

        # Check if the admin user exists and the password is correct
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return {'access_token': access_token}, 200

        return {'message': 'Invalid admin credentials'}, 401

@api.route('/logout')
class UserLogout(Resource):
    @jwt_required()
    @api.doc(security='Bearer Auth')  # Require Bearer Auth
    def post(self):
        jti = get_jwt()['jti']
        blacklist.add(jti)  # Add the token to the blacklist
        return {'message': 'Successfully logged out'}, 200


@api.route('/register')
class UserRegister(Resource):
    @api.expect(register_model)
    def post(self):
        """ Register a new user """
        data = api.payload
        
        # Check a valid email
        if not User.is_valid_email(data['email']):
            return {'message': 'Invalid email format'}, 400

        # Check if user already exists
        existing_user = User.query.filter((User.username == data['username']) | (User.email == data['email'])).first()
        if existing_user:
            return {'message': 'Username or email already taken'}, 400

        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        new_user.set_password(data['password'])  # Hash the password

        # Save to database
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User registered successfully!'}, 201