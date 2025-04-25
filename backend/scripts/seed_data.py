from faker import Faker
from models import db
from models.user import User
from models.complaint import Complaint
from services.classification import categorize_complaint
from services.recommendation_rag import chat_with_model
from models.sub_category import SubCategory
from models.department import Department
import random
import pandas as pd
from datetime import datetime
fake = Faker()

def generate_fake_data(num_users=5, complaints_per_user=3):
    """Generate fake users and complaints with AI responses"""
    complaint_templates = [
        "I have not received my order #{} yet. It's been {} days.",
        "The product I received is damaged. Order number #{}.",
        "I need a refund for order #{}, wrong item received.",
        "My account was charged twice for order #{}.",
        "Cannot access my account after {} attempts.",
        "The delivery address for order #{} is incorrect.",
        "The shipping is taking too long for order #{}.",
        "Product quality issues with my recent purchase #{}."
    ]
    
    complaint_templates_2 = [
        "Customer service was unhelpful with order #{}.",
        "Website error prevented me from completing order #{}.",
        "Missing parts in my delivery for order #{}.",
        "Received expired product from order #{}.",
        "Size/color doesn't match the description for order #{}.",
        "Technical issues with the app after {} updates.",
        "Billing discrepancy found in order #{}.",
        "Products arrived in poor packaging for order #{}."
    ]

    try:
        # Create fake users
        created_users = []
        for _ in range(num_users):
            user = User(
                username=fake.user_name(),
                email=fake.email(),
                role="client"
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
            created_users.append(user)
        
        db.session.commit()
        print(f"Created {len(created_users)} users")

        # Get all departments for random assignment
        departments = Department.query.all()
        if not departments:
            print("No departments found!")
            return "Error: No departments available"
        complaints_list=[]
        # Create complaints for each user
        total_complaints = 0
        for user in created_users:
            for _ in range(complaints_per_user):
                # Generate complaint text
                complaint_text = random.choice(complaint_templates).format(
                    fake.random_number(digits=6),
                    random.randint(2, 30)
                )

                # Get random department and its subcategories
                department = random.choice(departments)
                subcategories = SubCategory.query.filter_by(department_id=department.id).all()
                
                if not subcategories:
                    continue
                
                subcategory = random.choice(subcategories)

                # Create complaint
                complaint = Complaint(
                    title=f"Issue: {complaint_text[:30]}...",
                    description=complaint_text,
                    category=department.name,
                    sub_category=subcategory.name,
                    user_id=user.id,
                    department_id=department.id,
                    ai_response=chat_with_model(complaint_text),
                    created_at=datetime.now() - pd.Timedelta(days=random.randint(1, 30)),  # Random date within the last 30 days
                )
                complaints_list.append(complaint)
                db.session.add(complaint)
                total_complaints += 1
                
            # Commit after each user's complaints
            db.session.commit()
            print(f"Added {complaints_per_user} complaints for user {user.username}")

        # Generate replies
        print("Generating replies...")
        result = generate_fake_replies(complaints_list)
        
        return f"Successfully created {num_users} users with total {total_complaints} complaints. {result}"

    except Exception as e:
        db.session.rollback()
        print(f"Error in generate_fake_data: {str(e)}")
        return f"Error generating fake data: {str(e)}"

def generate_fake_replies(fake_user_complaints):
    """Generate fake replies for existing complaints from fake users"""
    
    # Get all complaints from fake users (excluding real users)
    # fake_user_complaints = (Complaint.query
    #                       .join(User)
    #                       .filter(User.email.like('%@example.%'))  # Basic email pattern to identify fake users
    #                       .filter(Complaint.admin_response.is_(None))  # Only unresponded complaints
    #                       .all())
    print(fake_user_complaints)
    response_templates = [
        "Thank you for bringing this to our attention. We have resolved issue #{} and processed your request.",
        "We apologize for the inconvenience. Your case #{} has been handled and resolved.",
        "Issue #{} has been investigated and appropriate action has been taken.",
        "We've processed your request #{}. Please allow 24-48 hours for the changes to take effect.",
        "Your complaint #{} has been addressed. A refund has been initiated.",
        "We've reviewed case #{} and implemented the necessary corrections."
    ]
    
    eval_options = ["good", "excellent", "fair", "needs_improvement"]
    
    try:
        for complaint in fake_user_complaints:
            # Generate fake response
            response = random.choice(response_templates).format(
                fake.random_number(digits=6)
            )
            
            # Set response details
            complaint.admin_response = response
            complaint.admin_eval_on_ai_response = random.choice(eval_options)
            complaint.response_at = complaint.created_at + pd.Timedelta(days=random.randint(1, 5))
            
           
        
        db.session.commit()
        return "Successfully generated fake replies"
    
    except Exception as e:
        db.session.rollback()
        return f"Error generating fake replies: {str(e)}"

# Usage example:
# from scripts.seed_data import generate_fake_data
# generate_fake_data(5, 3)  # Creates 5 users with 3 complaints each
