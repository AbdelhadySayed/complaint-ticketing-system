import random
from datetime import datetime, timedelta
from faker import Faker
from werkzeug.security import generate_password_hash
from models import db
from models.user import User
from models.complaint import Complaint
from models.department import Department

fake = Faker()

# Configuration
NUM_CLIENTS = 20
NUM_COMPLAINTS = 100


# Categories and subcategories mapped to existing departments
CATEGORY_MAP = {
    'ACCOUNT': ['edit_account', 'switch_account', 'account_registration_problems'],
    'ORDER': ['cancel_order', 'place_order', 'change_order'],
    'REFUND': ['track_refund', 'check_refund_policy'],
    'INVOICE': ['check_invoice', 'get_invoice'],
    'CONTACT': ['contact_customer_service', 'contact_human_agent'],
    'PAYMENT': ['check_payment_methods', 'payment_issue'],
    'FEEDBACK': ['feedback_complaint', 'feedback_review'],
    'DELIVERY': ['delivery_period', 'delivery_options'],
    'SHIPPING': ['set_up_shipping_address', 'change_shipping_address'],
    'SUBSCRIPTION': ['newsletter_subscription'],
    'CANCEL': ['check_cancellation_fee']
}


AI_RESPONSES = [
    "We're looking into your issue and will get back to you shortly.",
    "Thank you for bringing this to our attention. We're working on a solution.",
    "We've received your complaint and are processing it now.",
    "Our team is reviewing your concern and will respond soon.",
    "We appreciate your feedback and are addressing your issue."
]

ADMIN_RESPONSES = [
    "We've resolved your issue. Please let us know if you need anything else.",
    "Your request has been processed successfully.",
    "We've forwarded your complaint to the relevant department.",
    "This matter has been escalated to our senior team for review.",
    "We've implemented a fix for this issue. Thank you for your patience.",
    "Your refund has been processed and should appear in 3-5 business days.",
    "We've updated your account settings as requested.",
    "The delivery has been rescheduled as per your request.",
    "We've canceled your order and issued a full refund.",
    "Your subscription has been updated successfully."
]

def create_clients():
    """Create only client users with role='client'"""
    print(f"Creating {NUM_CLIENTS} client users...")
    
    for _ in range(NUM_CLIENTS):
        while True:  # Ensure unique username/email
            username = fake.user_name()
            email = fake.email()
            if not User.query.filter((User.username == username) | (User.email == email)).first():
                break
                
        user = User(
            username=username,
            email=email,
            role="client",
            department_id=None
        )
        user.set_password("test123")  # Simple password for testing
        db.session.add(user)
    
    db.session.commit()

def create_complaints():
    """Create test complaints linked to client users"""
    print(f"Creating {NUM_COMPLAINTS} complaints...")
    
    clients = User.query.filter_by(role="client").all()
    departments = Department.query.all()
    
    if not clients:
        raise ValueError("No client users found. Create users first.")
    
    for _ in range(NUM_COMPLAINTS):
        user = random.choice(clients)
        category = random.choice(list(CATEGORY_MAP.keys()))
        sub_category = random.choice(CATEGORY_MAP[category])
        
        # Find matching department
        department = next(
            (d for d in departments if d.branch == sub_category),
            None
        )
        
        created_at = fake.date_time_between(start_date='-60d', end_date='now')
        has_response = random.random() < 0.8  # 80% have responses
        
        complaint = Complaint(
            title=fake.sentence(nb_words=6),
            description=fake.paragraph(nb_sentences=3),
            category=category,
            sub_category=sub_category,
            ai_response=random.choice(AI_RESPONSES),
            admin_response=random.choice(ADMIN_RESPONSES) if has_response else None,
            created_at=created_at,
            response_at=created_at + timedelta(hours=random.randint(1, 72)) if has_response else None,
            user_id=user.id,
            department_id=department.id if department else None
        )
        db.session.add(complaint)
    
    db.session.commit()

def clean_test_data():
    """Remove only test data (clients + complaints)"""
    print("Cleaning test data...")
    Complaint.query.delete()
    User.query.filter_by(role="client").delete()
    db.session.commit()

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    
    with app.app_context():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--clean', action='store_true', help='Clean test data')
        args = parser.parse_args()
        
        if args.clean:
            clean_test_data()
            print("Cleaned all test clients and complaints")
        else:
            create_clients()
            create_complaints()
            print(f"""
            Successfully created:
            - {NUM_CLIENTS} client users (password: 'test123')
            - {NUM_COMPLAINTS} test complaints
            """)