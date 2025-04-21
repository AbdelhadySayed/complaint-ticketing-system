from flask import request
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.complaint import Complaint
from models.user import User
from models.department import Department
from models import db
# from services.recommendation import generate_response
from services.classification import categorize_complaint
from datetime import datetime
from sqlalchemy import desc
from services.recommender import chat_with_model
import pandas as pd
from services.vector import add_reply_to_chromadb
from models.sub_category import SubCategory
# Load mappings using pandas
categories_df = pd.read_csv('categories_to_departments.csv')
intents_df = pd.read_csv('intents_to_departments.csv')

# Create dictionaries for quick lookup
category_to_department = dict(zip(categories_df['Category'], categories_df['Department']))
intent_to_department = dict(zip(intents_df['Intent'], intents_df['Department']))


complaint_ns = Namespace('complaint', description='Complaint operations')

# Complaint model used by the user to add new complaint
complaint_model = complaint_ns.model('Complaint', {
    'number_of_complaints': fields.Integer(
        required=True,
        description='Complaint number (must be 1 or 2 only)',
    ),
    'title': fields.String(required=True),
    'description': fields.String(required=True)
})

# For client satisfaction (user-submitted)
satisfaction_model = complaint_ns.model('Satisfaction', {
    'satisfaction': fields.String(
        required=True,
        description='User satisfaction level (e.g., "satisfied", "neutral", "unsatisfied")',
        example="satisfied"
    )
})


# Model for responding to complaints and evaluation of ai response (submitted by department responsibles)
response_model = complaint_ns.model('Response', {
    'department_response': fields.String(required=True),
    'admin_eval_on_ai_response': fields.String(required=True, description='Department feedback on the AI response (e.g., "good", "poor")',
                                               example="good")
})


@complaint_ns.route('/addcomplaint')
class AddComplaint(Resource):
    @complaint_ns.expect(complaint_model)
    @complaint_ns.doc(security='Bearer Auth')
    @jwt_required()
    def post(self):
        """Submit a complaint by the user"""
        user_id = int(get_jwt_identity())
        data = complaint_ns.payload
        number = data["number_of_complaints"]

        if number not in [1, 2]:
            return {'message': 'number_of_complaint must be either 1 or 2'}, 400

        title = data["title"]
        description = data["description"]
        if not description:
            return {'message': 'Complaint not found'}, 404

        # Classify the complaint using the model
        sub_category = categorize_complaint(description)

        # Map sub_category to department using both mappings
        subcategory = SubCategory.query.filter_by(name=sub_category).first()
        department = subcategory.department
        
        if department is None:
            department=Department.query.filter_by(name="PENDING").first()
       

        # Generate AI response
        ai_response = chat_with_model(description)

        # Create a new complaint with default values
        new_complaint = Complaint(
            title=data['title'],
            description=data['description'],
            category=department.name,
            sub_category=sub_category,
            user_id=user_id,
            department_id=department.id,
            ai_response=ai_response
        )
        db.session.add(new_complaint)
        db.session.commit()

        return {
            "id": new_complaint.id,
            "title": title,
            "description": description,
            "response": ai_response,
            "category": department.name,
            "sub_category": sub_category
        }, 201

@complaint_ns.route('/usercomplaints')
class UserComplaints(Resource):
    @jwt_required()
    def get(self):
        """Retrieve all complaints submitted by the logged-in user."""
        current_user_id = int(get_jwt_identity())
        complaints = Complaint.query.filter_by(user_id=current_user_id).all()

        return [{
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'category': c.category,
            'sub_category': c.sub_category,
            'ai_response': c.ai_response,
            'admin_response': c.admin_response,
            'client_satisfaction': c.client_satisfaction,
            'admin_eval_on_ai_response': c.admin_eval_on_ai_response,
            'department_id': c.department_id,
            'created_at': c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'response_at': c.response_at.strftime("%Y-%m-%d %H:%M:%S") if c.response_at else None
        } for c in complaints], 200


@complaint_ns.route('/setsatisfaction/<int:complaint_id>')
class SetSatisfaction(Resource):
    @complaint_ns.expect(satisfaction_model)
    @jwt_required()
    def post(self, complaint_id):
        """Submit user satisfaction for a complaint."""
        current_user_id = int(get_jwt_identity())
        complaint = Complaint.query.filter_by(
            id=complaint_id, user_id=current_user_id).first()

        if not complaint:
            return {'message': 'Complaint not found or unauthorized'}, 404

        data = complaint_ns.payload
        complaint.client_satisfaction = data['satisfaction']
        db.session.commit()

        return {'message': 'Satisfaction submitted successfully!'}, 200


@complaint_ns.route('/respondtocomplaint/<int:complaint_id>')
class RespondToComplaint(Resource):
    @complaint_ns.expect(response_model)
    @jwt_required()
    def post(self, complaint_id):
        """Allow department users to respond to complaints assigned to their department."""
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or "department" not in user.role.split("_"):
            return {'message': 'Unauthorized: Only department users can respond to complaints'}, 403

        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return {'message': 'Complaint not found'}, 404

        if complaint.category != user.role[:-11]:
            return {'message': 'Unauthorized: This complaint is not assigned to your department'}, 403

        data = complaint_ns.payload
        complaint.admin_response = data['department_response']
        complaint.admin_eval_on_ai_response = data['admin_eval_on_ai_response']
        complaint.response_at = datetime.now()
        db.session.commit()
        # Add the response to the ChromaDB
        add_reply_to_chromadb(
            instruction=complaint.description,
            response=data['department_response'],
            category=complaint.category,
            intent=complaint.sub_category
        )
        return {'message': 'Response added successfully'}, 200


@complaint_ns.route('/departmentcomplaints')
class DepartmentComplaints(Resource):
    @jwt_required()
    def get(self):
        """Retrieve all complaints assigned to the department of the logged-in department user."""
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user:
            return {'message': 'Unauthorized: Only department users can access this'}, 403

        complaints = Complaint.query.filter_by(category=user.role[:-11]).all()

        return [{
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'category': c.category,
            'sub_category': c.sub_category,
            'ai_response': c.ai_response,
            'admin_response': c.admin_response,
            'client_satisfaction': c.client_satisfaction,
            'admin_eval_on_ai_response': c.admin_eval_on_ai_response,
            'department_id': c.department_id,
            'created_at': c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'response_at': c.response_at.strftime("%Y-%m-%d %H:%M:%S") if c.response_at else None
        } for c in complaints], 200


@complaint_ns.route('/allcomplaints')
class AllComplaints(Resource):
    @jwt_required()
    # @api.doc(security='Bearer Auth')  # Require Bearer Auth
    def get(self):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        # if not user.is_admin:
        #     return {'message': 'Unauthorized'}, 403
        if user.role == "client":
            complaints = user.complaints
        elif user.role == "admin":  
            query = Complaint.query
            start_date = datetime.strptime(request.args.get(
                "startDate"), "%Y-%m-%dT%H:%M") if request.args.get("startDate") else None
            end_date = datetime.strptime(request.args.get(
                "endDate"), "%Y-%m-%dT%H:%M") if request.args.get("endDate") else None
            # 3. Convert to DataFrame and clean data
            print(start_date, end_date)
            query = query.filter(Complaint.created_at >= start_date) if start_date else query
            query = query.filter(Complaint.created_at <= end_date) if end_date else query
            complaints = query.all()
        else:
            complaints = user.department.complaints
        return [{
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'category': c.category,
            "sub_category": c.sub_category,
            'ai_response': c.ai_response,
            'admin_response': c.admin_response,
            'user_id': c.user_id,
            'department_id': c.department_id

        } for c in complaints], 200
