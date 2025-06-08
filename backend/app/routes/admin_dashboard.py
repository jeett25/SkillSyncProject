from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.student import Student
from app.models.project import Project
from app.models.skill import Skill
from app.models.resume_upload import Resume
from app import db
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user_model = User(db)
        user = user_model.find_by_id(user_id)
        
        if not user or user.get('role') != 'admin':
            return {'message': 'Access denied. Admin privileges required.'}, 403
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    try:
        # Initialize models
        user_model = User(db)
        student_model = Student(db)
        project_model = Project(db)
        skill_model = Skill(db)
        resume_model = Resume(db)
        
        # Get basic statistics
        total_users = user_model.get_user_count()
        total_students = student_model.get_student_count()
        total_projects = project_model.get_total_project_count()
        total_skills = skill_model.get_total_skill_count()
        
        # Get resume statistics
        resume_stats = resume_model.get_resume_stats()
        
        # Get recent activities (you might want to implement an activity log)
        recent_users = user_model.get_recent_users(5)
        recent_projects = project_model.get_recent_projects(5)
        
        # Convert ObjectIds to strings for JSON serialization
        for user in recent_users:
            user['_id'] = str(user['_id'])
        
        for project in recent_projects:
            project['_id'] = str(project['_id'])
        
        dashboard_data = {
            'statistics': {
                'total_users': total_users,
                'total_students': total_students,
                'total_projects': total_projects,
                'total_skills': total_skills,
                'total_resumes': resume_stats['total_resumes'],
                'parsed_resumes': resume_stats['parsed_resumes'],
                'unparsed_resumes': resume_stats['unparsed_resumes']
            },
            'charts': {
                'top_skills': resume_stats['top_skills'][:10],  # Top 10 skills
                'user_growth': [],  # Implement user growth over time
                'project_categories': []  # Implement project categorization
            },
            'recent_activity': {
                'recent_users': recent_users,
                'recent_projects': recent_projects
            }
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        print(f"Error in admin_dashboard: {str(e)}")
        return {'message': f'Error fetching admin dashboard data: {str(e)}'}, 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        user_model = User(db)
        users = user_model.get_all_users()
        
        # Convert ObjectIds to strings and remove sensitive data
        for user in users:
            user['_id'] = str(user['_id'])
            user.pop('password', None)  # Remove password hash
        
        return jsonify(users), 200
        
    except Exception as e:
        print(f"Error in get_all_users: {str(e)}")
        return {'message': f'Error fetching users: {str(e)}'}, 500

@admin_bp.route('/projects/all', methods=['GET'])
@admin_required
def get_all_projects():
    try:
        project_model = Project(db)
        projects = project_model.get_all_projects()
        
        # Convert ObjectIds to strings
        for project in projects:
            project['_id'] = str(project['_id'])
            project['id'] = str(project['_id'])
        
        return jsonify(projects), 200
        
    except Exception as e:
        print(f"Error in get_all_projects: {str(e)}")
        return {'message': f'Error fetching projects: {str(e)}'}, 500

@admin_bp.route('/skills/analytics', methods=['GET'])
@admin_required
def get_skills_analytics():
    try:
        skill_model = Skill(db)
        
        # Get skill level distribution
        skill_levels = skill_model.get_skill_level_distribution()
        
        # Get most popular skills
        popular_skills = skill_model.get_popular_skills(20)
        
        # Get skill trends (skills added over time)
        skill_trends = skill_model.get_skill_trends()
        
        analytics_data = {
            'skill_levels': skill_levels,
            'popular_skills': popular_skills,
            'skill_trends': skill_trends,
            'total_unique_skills': len(popular_skills)
        }
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        print(f"Error in get_skills_analytics: {str(e)}")
        return {'message': f'Error fetching skills analytics: {str(e)}'}, 500

@admin_bp.route('/resumes', methods=['GET'])
@admin_required
def get_all_resumes():
    try:
        resume_model = Resume(db)
        resumes = resume_model.get_all_resumes()
        
        # Convert ObjectIds to strings and remove file paths
        for resume in resumes:
            resume['_id'] = str(resume['_id'])
            resume.pop('file_path', None)  # Remove file path for security
        
        return jsonify(resumes), 200
        
    except Exception as e:
        print(f"Error in get_all_resumes: {str(e)}")
        return {'message': f'Error fetching resumes: {str(e)}'}, 500
@admin_bp.route('/students', methods=['GET'])
@admin_required
def get_all_students():
    """Get all student profiles for admin dashboard"""
    try:
        student_model = Student(db)
        students = student_model.get_all_students()
        
        # Convert ObjectIds to strings for JSON serialization
        for student in students:
            student['_id'] = str(student['_id'])
            if 'user_id' in student:
                student['user_id'] = str(student['user_id'])
        
        return jsonify(students), 200
        
    except Exception as e:
        print(f"Error in get_all_students: {str(e)}")
        return {'message': f'Error fetching students: {str(e)}'}, 500


@admin_bp.route('/analytics/overview', methods=['GET'])
@admin_required
def get_analytics_overview():
    try:
        # This endpoint provides data for charts and visualizations
        user_model = User(db)
        project_model = Project(db)
        skill_model = Skill(db)
        resume_model = Resume(db)
        
        # Get user registration trends (last 6 months)
        user_trends = user_model.get_user_registration_trends()
        
        # Get project creation trends
        project_trends = project_model.get_project_creation_trends()
        
        # Get skill usage statistics
        skill_stats = skill_model.get_skill_usage_stats()
        
        # Get technology stack popularity
        tech_stack = resume_model.get_technology_stack_stats()
        
        overview_data = {
            'user_trends': user_trends,
            'project_trends': project_trends,
            'skill_distribution': skill_stats,
            'tech_stack': tech_stack,
            'growth_metrics': {
                'monthly_user_growth': user_model.get_monthly_growth(),
                'monthly_project_growth': project_model.get_monthly_growth(),
                'skill_adoption_rate': skill_model.get_adoption_rate()
            }
        }
        
        return jsonify(overview_data), 200
        
    except Exception as e:
        print(f"Error in get_analytics_overview: {str(e)}")
        return {'message': f'Error fetching analytics overview: {str(e)}'}, 500