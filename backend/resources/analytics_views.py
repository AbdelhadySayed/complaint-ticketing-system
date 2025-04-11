from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.complaint import Complaint
from models.user import User
from models.department import Department
from models import db
from datetime import datetime, timedelta
import plotly.graph_objs as go
import pandas as pd
from flask import request
import numpy as np
import json
from flask_compress import Compress
from flask import Flask
import plotly.io as pio
import os
from pathlib import Path


analytics_ns = Namespace('analytics', description='Business analytics operations')

# Create debug figures directory
DEBUG_FIGURES_DIR = Path("debug_figures")
DEBUG_FIGURES_DIR.mkdir(exist_ok=True)

metrics_model = analytics_ns.model('Metrics', {
    'total_complaints': fields.Integer,
    'responded_complaints': fields.Integer,
    'pending_complaints': fields.Integer,
    'avg_response_time': fields.Float,
    'median_response_time': fields.Float,
    'response_rate': fields.Float
})

dashboard_response_model = analytics_ns.model('DashboardResponse', {
    'graphs': fields.Raw(description='Dictionary of Plotly figures'),
    'metrics': fields.Nested(metrics_model)
})


def _convert_to_serializable(obj):
    """Recursively convert objects to serializable types"""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (datetime, pd.Timestamp)):
        return obj.strftime('%d/%m/%Y')  # DD/MM/YYYY format
    elif isinstance(obj, (list, tuple)):
        return [_convert_to_serializable(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: _convert_to_serializable(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        return _convert_to_serializable(obj.__dict__)
    elif isinstance(obj, (pd.Timedelta, timedelta)):
        return str(obj)
    return obj

def _create_serializable_figure(fig):
    """Convert Plotly figure to a serializable dictionary and remove bloat"""
    fig_dict = fig.to_dict()
    # Remove redundant template data to reduce payload size
    if "layout" in fig_dict and "template" in fig_dict["layout"]:
        del fig_dict["layout"]["template"]
    return _convert_to_serializable(fig_dict)

# Figure saving function
def _save_debug_figure(fig, filename):
    """Helper to save figures for debugging"""
    filepath = DEBUG_FIGURES_DIR / f"{filename}.html"
    pio.write_html(fig, filepath, auto_open=False)


@analytics_ns.route('/admin/dashboard')
class AdminDashboard(Resource):
    @analytics_ns.marshal_with(dashboard_response_model)
    @analytics_ns.doc(params={
        'start_date': 'Start date (DD/MM/YYYY)',
        'end_date': 'End date (DD/MM/YYYY)'
    })
    @jwt_required()
    def get(self):
        """Get analytics dashboard data with optional date filtering"""
        # 1. Verify admin access
        current_user = User.query.get(get_jwt_identity())
        if not current_user or not current_user.is_admin:
            return {'message': 'Admin access required'}, 403
        
        # 2. Parse and validate date parameters
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%d/%m/%Y') if 'start_date' in request.args else datetime.strptime("1/11/2025", '%d/%m/%Y')
            end_date = datetime.strptime(request.args.get('end_date'), '%d/%m/%Y') if 'end_date' in request.args else  datetime.now()
            
            if start_date and end_date and start_date > end_date:
                return {'message': 'Start date must be before end date'}, 400
        except ValueError:
            return {'message': 'Invalid date format. Use DD/MM/YYYY'}, 400
        
        # 3. Query complaints with date filters
        query = Complaint.query
        if start_date:
            query = query.filter(Complaint.created_at >= start_date)
        if end_date:
            query = query.filter(Complaint.created_at <= end_date + timedelta(days=1))
        
        complaints = query.all()
        
        # 4. Convert to DataFrame and clean data
        df = pd.DataFrame([{
            'id': c.id,
            'category': c.category,
            'sub_category': c.sub_category,
            'created_at': c.created_at,
            'response_at': c.response_at,
            'department_id': c.department_id,
            'admin_response': c.admin_response,
            'admin_eval_on_ai_response': c.admin_eval_on_ai_response,
            'client_satisfaction':c.client_satisfaction
        } for c in complaints])
        
        # save df
        df.to_csv("complaints.csv", index=False)
        
        # 5. Calculate metrics
        df['response_time'] = (df['response_at'] - df['created_at']).dt.total_seconds() / 3600
        df['has_response'] = df['admin_response'].notnull()

        # Clean NaN values to prevent chart errors
        df = df.dropna(subset=['response_time', 'department_id'])
        
        responded = df['has_response'].sum()
        total = len(df)
        
        metrics = {
            'total_complaints': int(total),
            'responded_complaints': int(responded),
            'pending_complaints': int(total - responded),
            'avg_response_time': float(df[df['has_response']]['response_time'].mean()),
            'median_response_time': float(df[df['has_response']]['response_time'].median()),
            'response_rate': float((responded / total * 100) if total > 0 else 0)
        }
        
        # 6. Generate and serialize figures 
        figures = {}
        if not df.empty:
            figures = {
                'status_distribution': self._create_status_chart(df),
                'response_time_by_dept': self._create_dept_response_chart(df),
                'complaints_by_category': self._create_category_chart(df),
                'top_subcategories': self._create_subcategory_chart(df),
                'complaints_over_time': self._create_timeseries_chart(df),
                'response_time_dist': self._create_histogram_chart(df)
            }
            figures = {k: _create_serializable_figure(v) for k, v in figures.items()}
        
        # 7. Return optimized response
        return {
            'graphs': figures,  # Direct dictionary
            'metrics': metrics
        }
    
    # Chart Generation Methods 
    def _create_status_chart(self, df):
        status_counts = df['has_response'].value_counts(normalize=True) * 100
        fig = go.Figure(go.Pie(
            labels=['Responded', 'Pending'],
            values=status_counts,
            hole=.3,
            textinfo='label+percent',
            marker=dict(colors=['#4CAF50', '#F44336'])  # Green for responded, red for pending
        ))
        fig.update_layout(
            title_text='Complaint Status Distribution',
            showlegend=True
        )
        _save_debug_figure(fig, "status_distribution")
        return fig
    
    def _create_dept_response_chart(self, df):
        dept_response = df[df['has_response']].groupby('department_id')['response_time'].mean().reset_index()
        dept_response['department_name'] = dept_response['department_id'].apply(
            lambda x: Department.query.get(x).name if x else 'Pending'
        )
        
        # Sort by response time for better visualization
        dept_response = dept_response.sort_values('response_time', ascending=False)
        
        # Create a color scale based on response time (longer times get warmer colors)
        max_time = dept_response['response_time'].max()
        colors = [
            f'hsl({int(120 * (1 - time/max_time))}, 70%, 50%)'  # Green to red gradient
            for time in dept_response['response_time']
        ]
        
        fig = go.Figure(go.Bar(
            x=dept_response['department_name'],
            y=dept_response['response_time'],
            text=dept_response['response_time'].round(1),
            textposition='auto',
            marker_color=colors,
            marker_line_color='rgba(0,0,0,0.5)',
            marker_line_width=1
        ))
        fig.update_layout(
            title_text='Average Response Time by Department',
            yaxis_title='Hours',
            xaxis_title='Department',
            plot_bgcolor='rgba(240,240,240,0.8)'
        )
        _save_debug_figure(fig, "dept_response")
        return fig
    
    def _create_category_chart(self, df):
        category_counts = df['category'].value_counts().reset_index()
        fig = go.Figure(go.Bar(
            x=category_counts['index'],
            y=category_counts['category'],
            text=category_counts['category'],
            textposition='auto',
            marker_color='#2196F3',  # Blue color
            marker_line_color='rgba(0,0,0,0.5)',
            marker_line_width=1
        ))
        fig.update_layout(
            title_text='Complaints by Category',
            yaxis_title='Count',
            xaxis_title='Category',
            plot_bgcolor='rgba(240,240,240,0.8)'
        )
        _save_debug_figure(fig, "category_distribution")
        return fig
    
    def _create_subcategory_chart(self, df):
        subcat_counts = df['sub_category'].value_counts().nlargest(10).reset_index()
        fig = go.Figure(go.Bar(
            x=subcat_counts['index'],
            y=subcat_counts['sub_category'],
            text=subcat_counts['sub_category'],
            textposition='auto',
            marker_color='#673AB7',  # Purple color
            marker_line_color='rgba(0,0,0,0.5)',
            marker_line_width=1
        ))
        fig.update_layout(
            title_text='Top 10 Complaint Sub-Categories',
            yaxis_title='Count',
            xaxis_title='Sub-Category',
            plot_bgcolor='rgba(240,240,240,0.8)'
        )
        _save_debug_figure(fig, "subcategories")
        return fig
    
    def _create_timeseries_chart(self, df):
        time_series = df.groupby(pd.Grouper(key='created_at', freq='D')).size().reset_index(name='count')
        time_series['created_at'] = time_series['created_at'].dt.strftime('%d/%m/%Y')
        fig = go.Figure(go.Scatter(
            x=time_series['created_at'],
            y=time_series['count'],
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#FF9800', width=2),  # Orange line
            marker=dict(color='#FF5722', size=8)  # Darker orange markers
        ))
        fig.update_layout(
            title_text='Complaints Over Time',
            yaxis_title='Daily Complaints',
            xaxis_title='Date',
            plot_bgcolor='rgba(240,240,240,0.8)'
        )
        _save_debug_figure(fig, "timeseries")
        return fig
    
    def _create_histogram_chart(self, df):
        fig = go.Figure(go.Histogram(
            x=df[df['has_response']]['response_time'],
            nbinsx=20,
            marker_color='#00BCD4',  # Cyan color
            marker_line_color='rgba(0,0,0,0.5)',
            marker_line_width=1
        ))
        fig.update_layout(
            title_text='Response Time Distribution',
            yaxis_title='Count',
            xaxis_title='Hours',
            plot_bgcolor='rgba(240,240,240,0.8)'
        )
        _save_debug_figure(fig, "response_histogram")
        return fig