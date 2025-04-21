from . import db


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationship with Complaint table
    complaints = db.relationship('Complaint', backref='department', lazy=True)
    
# Insert predefined departments
def insert_departments():

    departments = ["PENDING", "Orders & Purchases", "Shipping & Delivery", "Returns & Refunds", "Billing & Invoices",
                   "Feedback & Community", "Customer Service", "Accounts & Access"]

    for dep in departments:
        if not Department.query.filter_by(name=dep).first():
            db.session.add(Department(name=dep))
    db.session.commit()
