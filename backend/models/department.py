from . import db

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(100), nullable=True, default="pending") # unique True
    
    # Relationship with Complaint table
    complaints = db.relationship('Complaint', backref='department', lazy=True)


# Insert predefined departments
def insert_departments():
    departments = [('PENDING', 'pending'), ('ACCOUNT', 'edit_account'), ('ACCOUNT', 'switch_account'), ('ACCOUNT', 'account_registration_problems'), ('ACCOUNT', 'create_account'), 
       ('ACCOUNT', 'delete_account'), ('ACCOUNT', 'account_recover_password'), ('CANCEL', 'check_cancellation_fee'), ('CONTACT', 'contact_customer_service'),
       ('CONTACT', 'contact_human_agent'), ('DELIVERY', 'delivery_period'), ('DELIVERY', 'delivery_options'), ('FEEDBACK', 'feedback_complaint'), 
       ('FEEDBACK', 'feedback_review'), ('INVOICE', 'check_invoice'), ('INVOICE', 'get_invoice'), ('ORDER', 'cancel_order'), ('ORDER', 'place_order'), 
       ('ORDER', 'change_order'), ('ORDER', 'track_order'), ('PAYMENT', 'check_payment_methods'), ('PAYMENT', 'payment_issue'), 
       ('REFUND', 'track_refund'), ('REFUND', 'check_refund_policy'), ('REFUND', 'get_refund'), ('SHIPPING', 'set_up_shipping_address'), 
       ('SHIPPING', 'change_shipping_address'), ('SUBSCRIPTION', 'newsletter_subscription')]

    for dep in departments:
        if not Department.query.filter_by(name=dep[0], branch=dep[1]).first():
            db.session.add(Department(name=dep[0], branch=dep[1]))
    db.session.commit()

    #departments = ["ACCOUNT", "ORDER", "REFUND", "INVOICE", "CONTACT", "PAYMENT", "FEEDBACK", "DELIVERY", "SHIPPING", "SUBSCRIPTION", "CANCEL","Pending"]
