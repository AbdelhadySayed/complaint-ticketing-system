from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.complaint import Complaint
from models.user import User
from models.department import Department
from models import db
from datetime import datetime, timedelta
import plotly.graph_objs as go
import pandas as pd
from flask import request, send_from_directory
import numpy as np
import json
from flask_compress import Compress
from flask import Flask
import plotly.io as pio
import os
from pathlib import Path

analytics_ns = Namespace('analytics', description='Business analytics operations')

# Create directories for HTML figures
HTML_FIGURES_DIR = Path("static/analytics_figures")
HTML_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

metrics_model = analytics_ns.model('Metrics', {
    'total_complaints': fields.Integer,
    'responded_complaints': fields.Integer,
    'pending_complaints': fields.Integer,
    'avg_response_time': fields.Float,
    'median_response_time': fields.Float,
    'response_rate': fields.Float
})

dashboard_response_model = analytics_ns.model('DashboardResponse', {
    'graph_urls': fields.Raw(description='Dictionary of HTML figure URLs'),
    'metrics': fields.Nested(metrics_model)
})

def _save_html_figure(fig, filename):
    """Save figure as HTML file and return its URL"""
    filepath = HTML_FIGURES_DIR / f"{filename}.html"
    pio.write_html(fig, filepath, auto_open=False, include_plotlyjs='cdn')
    return f"/static/analytics_figures/{filename}.html"

@analytics_ns.route('/admin/dashboard')
class AdminDashboard(Resource):
    @analytics_ns.marshal_with(dashboard_response_model)
    # @jwt_required()
    def get(self):
        """Get analytics dashboard data with HTML figures"""
        # 1. Verify admin access
        # current_user = User.query.get(get_jwt_identity())
        # if not current_user or not current_user.is_admin:
        #     return {'message': 'Admin access required'}, 403
        
        # 2. Query complaints
        query = Complaint.query
        complaints = query.all()
        
        # 3. Convert to DataFrame and clean data
        df = pd.DataFrame([{
            'id': c.id,
            'category': c.category,
            'sub_category': c.sub_category,
            'created_at': c.created_at,
            'response_at': c.response_at,
            'department_id': c.department_id,
            'admin_response': c.admin_response,
            'admin_eval_on_ai_response': c.admin_eval_on_ai_response,
            'client_satisfaction': c.client_satisfaction
        } for c in complaints])
        
        # 4. Calculate metrics - handle "Pending" responses
        df['has_response'] = df['admin_response'] != "Pending"  # True if not "Pending"
        print(df["has_response"])
        responded = df['has_response'].sum()
        pending = len(df) - responded
        print(pending, responded)
        df['response_time'] = (df['response_at'] - df['created_at']).dt.total_seconds() / 3600
        #df = df.dropna(subset=['response_time', 'department_id'])
        
        #responded = df['has_response'].sum()
        total = len(df)
        print(total, responded)

        metrics = {
            'total_complaints': int(total),
            'responded_complaints': int(responded),
            'pending_complaints': int(pending),
            'avg_response_time': float(df[df['has_response']]['response_time'].mean()) if responded > 0 else 0,
            'median_response_time': float(df[df['has_response']]['response_time'].median()) if responded > 0 else 0,
            'response_rate': float((responded / total * 100) if total > 0 else 0)
        }
        
        # 5. Generate figures and save as HTML files
        graph_urls = {}
        if not df.empty:
            figures = {
                'status_distribution': self._create_status_chart(df),
                'response_time_by_dept': self._create_dept_response_chart(df),
                'complaints_by_category': self._create_category_chart(df),
                'top_subcategories': self._create_subcategory_chart(df),
                'complaints_over_time': self._create_timeseries_chart(df),
                'response_time_dist': self._create_histogram_chart(df)
            }
            graph_urls = {k: _save_html_figure(v, k) for k, v in figures.items()}
        
        return {
            'graph_urls': graph_urls,
            'metrics': metrics
        }
    
    # Chart Generation Methods
    def _create_status_chart(self, df):
        # Count actual "Pending" strings in admin_response
        pending_count = (df['admin_response'] == "Pending").sum()
        responded_count = len(df) - pending_count
        labels = ['Responded', 'Pending']
        values = [responded_count, pending_count]

        fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        textinfo='label+percent',
        marker=dict(colors=['#4CAF50', '#F44336'])  # Green for responded, red for pending
        ))

        fig.update_layout(
        title_text='Complaint Status Distribution',
        showlegend=True
        )
        return fig
    
    def _create_dept_response_chart(self, df):
        # Only show departments with actual responses (not "Pending")
        dept_response = df[df['has_response']].groupby('department_id')['response_time'].mean().reset_index()
        dept_response['department_name'] = dept_response['department_id'].apply(
            lambda x: Department.query.get(x).name if x else 'Unknown'
        )
        dept_response = dept_response.sort_values('response_time', ascending=False)
        
        # Handle empty case
        if dept_response.empty:
            fig = go.Figure()
            fig.update_layout(
                title_text='Average Response Time by Department',
                yaxis_title='Hours',
                xaxis_title='Department',
                plot_bgcolor='rgba(240,240,240,0.8)'
            )
            return fig
            
        max_time = dept_response['response_time'].max()
        colors = [
            f'hsl({int(120 * (1 - time/max_time))}, 70%, 50%)'
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
        return fig
    
    def _create_category_chart(self, df):
        category_counts = df['category'].value_counts().reset_index()
        fig = go.Figure(go.Bar(
            x=category_counts['category'],
            y=category_counts['count'],
            text=category_counts['category'],
            textposition='auto',
            marker_color='#2196F3',
            marker_line_color='rgba(0,0,0,0.5)',
            marker_line_width=1
        ))
        fig.update_layout(
            title_text='Complaints by Category',
            yaxis_title='Count',
            xaxis_title='Category',
            plot_bgcolor='rgba(240,240,240,0.8)'
        )
        return fig
    
    def _create_subcategory_chart(self, df):
        subcat_counts = df['sub_category'].value_counts().nlargest(10).reset_index()
        fig = go.Figure(go.Bar(
            x=subcat_counts['sub_category'],
            y=subcat_counts['count'],
            text=subcat_counts['sub_category'],
            textposition='auto',
            marker_color='#673AB7',
            marker_line_color='rgba(0,0,0,0.5)',
            marker_line_width=1
        ))
        fig.update_layout(
            title_text='Top 10 Complaint Sub-Categories',
            yaxis_title='Count',
            xaxis_title='Sub-Category',
            plot_bgcolor='rgba(240,240,240,0.8)'
        )
        return fig
    
    def _create_timeseries_chart(self, df):
        time_series = df.groupby(pd.Grouper(key='created_at', freq='D')).size().reset_index(name='count')
        time_series['created_at'] = time_series['created_at'].dt.strftime('%d/%m/%Y')
        fig = go.Figure(go.Scatter(
            x=time_series['created_at'],
            y=time_series['count'],
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#FF9800', width=2),
            marker=dict(color='#FF5722', size=8)
        ))
        fig.update_layout(
            title_text='Complaints Over Time',
            yaxis_title='Daily Complaints',
            xaxis_title='Date',
            plot_bgcolor='rgba(240,240,240,0.8)'
        )
        return fig
    
    def _create_histogram_chart(self, df):
        # Only show response times for actual responses (not "Pending")
        response_times = df[df['has_response']]['response_time']
        
        fig = go.Figure(go.Histogram(
            x=response_times,
            nbinsx=20,
            marker_color='#00BCD4',
            marker_line_color='rgba(0,0,0,0.5)',
            marker_line_width=1
        ))
        fig.update_layout(
            title_text='Response Time Distribution',
            yaxis_title='Count',
            xaxis_title='Hours',
            plot_bgcolor='rgba(240,240,240,0.8)'
        )
        return fig