import time
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

analytics_ns = Namespace(
    'analytics', description='Business analytics operations')

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
    try:
        filepath = HTML_FIGURES_DIR / f"{filename}.html"
        fig.update_layout(
            plot_bgcolor='#717078',
            paper_bgcolor='#717078',
            font=dict(color='white'),
            xaxis=dict(showgrid=False, color='white'),
            yaxis=dict(showgrid=False, color='white')
        )
        
        # Set config to include necessary plotly dependencies
        config = {'responsive': True, 'displaylogo': False}
        pio.write_html(
            fig, 
            filepath, 
            auto_open=False,
            include_plotlyjs='cdn',  # Use CDN for plotly.js
            full_html=True,  # Include full HTML with proper headers
            config=config
        )
        return f"/static/analytics_figures/{filename}.html"
    except Exception as e:
        print(f"Error saving figure: {str(e)}")
        return None


@analytics_ns.route('/admin/dashboard')
class AdminDashboard(Resource):
    @analytics_ns.marshal_with(dashboard_response_model)
    # @jwt_required()
    def get(self):
        """Get analytics dashboard data with HTML figures"""
        try:
            # 2. Query complaints with optimized filtering
            query = Complaint.query

            if request.args.get("startDate"):
                start_date = datetime.strptime(request.args.get("startDate"), "%Y-%m-%dT%H:%M")
                query = query.filter(Complaint.created_at >= start_date)

            if request.args.get("endDate"):
                end_date = datetime.strptime(request.args.get("endDate"), "%Y-%m-%dT%H:%M")
                query = query.filter(Complaint.created_at <= end_date)

            # Add index hint and eager loading for better performance
            complaints = query.order_by(Complaint.created_at.desc()).all()

            if not complaints:
                return {
                    'graph_urls': {},
                    'metrics': {
                        'total_complaints': 0,
                        'responded_complaints': 0,
                        'pending_complaints': 0,
                        'avg_response_time': 0,
                        'median_response_time': 0,
                        'response_rate': 0
                    }
                }

            # Continue with existing DataFrame creation and processing
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
            df['has_response'] = df['admin_response'] != "PENDING"
            responded = df['has_response'].sum()
            pending = len(df) - responded
            df['response_at'] = pd.to_datetime(df['response_at'], errors='coerce')
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            df['response_time'] = (df['response_at'] - df['created_at']).dt.total_seconds() / 3600
            total = len(df)

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
        except Exception as e:
            print(f"Error in AdminDashboard GET: {str(e)}")
            return {'message': 'An error occurred while processing the request'}, 500

    # Chart Generation Methods
    def _create_status_chart(self, df):
        pending_count = (df['admin_response'] == "PENDING").sum()
        responded_count = len(df) - pending_count
        labels = ['Responded', 'Pending']
        values = [responded_count, pending_count]

        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            textinfo='label+percent',
            marker=dict(colors=['#4CAF50', '#F44336'])
        ))

        fig.update_layout(
            title_text='Complaint Status Distribution',
            showlegend=True
        )
        return fig

    def _create_dept_response_chart(self, df):
        dept_response = df[df['has_response']].groupby(
            'department_id')['response_time'].mean().reset_index()
        dept_response = dept_response.dropna(subset=['response_time'])

        dept_response['department_name'] = dept_response['department_id'].apply(
            lambda x: Department.query.get(x).name if x else 'Unknown'
        )
        dept_response = dept_response.sort_values('response_time', ascending=False)

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
        if pd.isna(max_time) or max_time == 0:
            colors = ['#2196F3'] * len(dept_response)
        else:
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
        subcat_counts = df['sub_category'].value_counts().nlargest(
            10).reset_index()
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
        time_series = df.groupby(pd.Grouper(
            key='created_at', freq='D')).size().reset_index(name='count')
        time_series['created_at'] = time_series['created_at'].dt.strftime(
            '%d/%m/%Y')
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
