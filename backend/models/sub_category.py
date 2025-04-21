from . import db
import pandas as pd
from models.department import Department
class SubCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)

    # Relationship with Complaint table
    department = db.relationship('Department', backref='sub_category', lazy=True)

    def __repr__(self):
        return f"<SubCategory {self.name}>"
    
    def add_sub_category():
        """Add a new sub-category."""
        df= pd.read_csv('intents_to_departments.csv')
        for index, row in df.iterrows():
            name=row["Intent"]
            if SubCategory.query.filter_by(name=name).first():
                continue
            department_id=Department.query.filter_by(name=row["Department"]).first().id
            new_sub_category = SubCategory(name=name, department_id=department_id)
            db.session.add(new_sub_category)
        db.session.commit()