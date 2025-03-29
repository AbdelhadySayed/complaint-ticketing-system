from . import db

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    branch = db.Column(db.String(100), nullable=True, default="pending") # unique True
    
    # Relationship with Complaint table
    complaints = db.relationship('Complaint', backref='department', lazy=True)


# Insert predefined departments
def insert_departments():
    departments = ["ACCOUNT", "ORDER", "REFUND", "INVOICE", "CONTACT", "PAYMENT", "FEEDBACK", "DELIVERY", "SHIPPING", "SUBSCRIPTION", "CANCEL","Pending"]
    for dep in departments:
        if not Department.query.filter_by(name=dep).first():
            db.session.add(Department(name=dep))
    db.session.commit()

