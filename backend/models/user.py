from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .department import Department  
import re

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default="client")  # Default role is "client"
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    #department = db.Column(db.String(50), default="client")

    # Relationships
    complaints = db.relationship('Complaint', backref='user', lazy=True)
    #department = db.relationship('Department', backref=db.backref('users', lazy=True))

    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == "admin"

    def set_password(self, password):
        """Hash the password and store it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def is_valid_email(email):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(email_regex, email) is not None




def insert_users():
    """Insert admin and department users into the database."""
    admin = User(
        username="admin",
        email="admin@comapny_domain.com",
        role="admin",
    )
    admin.set_password("admin123")
    db.session.add(admin)

    department_categories = [
        "ACCOUNT", "ORDER", "REFUND", "INVOICE", "CONTACT",
        "PAYMENT", "FEEDBACK", "DELIVERY", "SHIPPING", "SUBSCRIPTION",
        "CANCEL", "Pending"
    ]

    users_data = [
        {
            "username": f"{dept.lower()}_user",
            "email": f"{dept.lower()}@company_domain.com",
            "password": "password123",
            "role": dept,
        }

        for dept in department_categories
    ]

    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data["email"]).first()
        if existing_user:
            print(f"User with email {user_data['email']} already exists. Skipping insertion.")
            continue  # Skip duplicate entry

        # Fetch department by name
        #department = Department.query.filter_by(name=user_data["department"]).first()
        #if not department:
        #    print(f"Department {user_data['department']} not found. Skipping user {user_data['email']}.")
        #   continue

        # Create new user
        new_user = User(
            username=user_data["username"],
            email=user_data["email"],
            #password_hash=set_password(user_data["password"]),  # Hash password
            role=user_data["role"] +"_department",
        )
        new_user.set_password("password123")  # Hashes the password before storing
        # Add and commit the new user
        db.session.add(new_user)

    try:
        db.session.commit()
        print("User insertion completed successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error inserting users: {e}")
