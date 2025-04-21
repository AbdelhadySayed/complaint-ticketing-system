from datetime import datetime
from . import db

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='PENDING')  # Default category
    sub_category = db.Column(db.String(50), default='PENDING')  # Default category
    ai_response = db.Column(db.Text, default='PENDING')     # AI response with default value
    admin_response = db.Column(db.Text, default='PENDING')  # department response manually added by department
    admin_eval_on_ai_response = db.Column(db.String(20), nullable=True) # department evaluation on ai response 
    client_satisfaction = db.Column(db.String(20), nullable=True) # client satiffaction 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Automatically set to current time
    response_at = db.Column(db.DateTime)  # Will be set when admin responds

    # Foreign key to User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Foreign key to Department table (default to None or a "Pending" department)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True, default=None)

    def __repr__(self):
        return f"<Complaint {self.title}>"


