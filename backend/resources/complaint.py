from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.complaint import Complaint
from models.user import User
from models.department import Department
from models import db
from services.recommendation import generate_response
from services.classification import categorize_complaint


api = Namespace('complaint', description='Complaint operations')

complaint_model = api.model('Complaint', {
    'title': fields.String(required=True),
    'description': fields.String(required=True)
})

@api.route('/addcomplaint')
class AddComplaint(Resource):
    @api.expect(complaint_model)
    @jwt_required()
    @api.doc(security='Bearer Auth')
    def post(self):
        user_id = get_jwt_identity()
        data = api.payload
        title = data["title"]
        description = data["description"]
        category = 'Pending' # to be changed to categorize_complaint(data['description'])
        ai_response = generate_response(description)
        department_id = None  # Default to None (or use the "Pending" department ID)

        # Create a new complaint with default values
        new_complaint = Complaint(
            title=data['title'],
            description=data['description'],
            category=category,
            user_id=user_id,
            department_id=department_id,  # Default to None or "Pending" department
            ai_response=ai_response
        )
        db.session.add(new_complaint)
        db.session.commit()

        # Assign the complaint to a department based on the category
        department = Department.query.filter_by(name=category).first()
        if department:
            new_complaint.department_id = department.id
        else:
            # If no department matches the category, assign it to the "Pending" department
            pending_department = Department.query.filter_by(name='Pending').first()
            if pending_department:
                new_complaint.department_id = pending_department.id

        # Update the complaint with the category and AI response
        #new_complaint.category = category
        #new_complaint.ai_response = ai_response
        db.session.commit()

        return {"title":title,
                "description":description,
                "response": ai_response,
                "category": category}, 201

@api.route('/usercomplaints/<int:user_id>')
class UserComplaints(Resource):
    @jwt_required()
    @api.doc(security='Bearer Auth')  # Require Bearer Auth
    def get(self, user_id):
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return {'message': 'Unauthorized'}, 403
        complaints = Complaint.query.filter_by(user_id=user_id).all()
        return [{
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'category': c.category,
            'ai_response': c.ai_response,
            'admin_response': c.admin_response,
            'department_id': c.department_id
        } for c in complaints], 200

@api.route('/allcomplaints')
class AllComplaints(Resource):
    @jwt_required()
    # @api.doc(security='Bearer Auth')  # Require Bearer Auth
    def get(self):
        current_user_id = get_jwt_identity()
        print(current_user_id)
        user = User.query.get(current_user_id)
        # if not user.is_admin:
        #     return {'message': 'Unauthorized'}, 403
        if user.role=="client":
            complaints = user.complaints
        else:
            complaints=Complaint.query.filter_by(department_id=user.department_id)

        return [{
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'category': c.category,
            'ai_response': c.ai_response,
            'admin_response': c.admin_response,
            'user_id': c.user_id,
            'department_id': c.department_id
        } for c in complaints], 200
    
    
@api.route('/departmentcomplaints/<int:department_id>')
class DepartmentComplaints(Resource):
    @jwt_required()
    @api.doc(security='Bearer Auth')  # Require Bearer Auth
    def get(self, department_id):
        department = Department.query.get(department_id)
        if not department:
            return {'message': 'Department not found'}, 404
        complaints = Complaint.query.filter_by(department_id=department_id).all()
        return [{
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'category': c.category,
            'ai_response': c.ai_response,
            'admin_response': c.admin_response,
            'user_id': c.user_id
        } for c in complaints], 200



@api.route('/respondtocomplaint/<int:complaint_id>')
class RespondToComplaint(Resource):
    @api.expect(api.model('Respond', {
        'admin_response': fields.String(required=True)
    }))
    @jwt_required()
    def post(self, complaint_id):
        # Ensure the user is an admin
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user.is_admin:
            return {'message': 'Unauthorized'}, 403

        # Get the complaint
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return {'message': 'Complaint not found'}, 404

        # Update the admin response and response time
        data = api.payload
        complaint.admin_response = data['admin_response']
        complaint.response_at = datetime.utcnow()  # Set the response time to now
        db.session.commit()

        return {'message': 'Response added successfully'}, 200