from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.student import Student
from app.models.project import Project
from app.models.skill import Skill
from app import db

dashboard_bp = Blueprint('dashboard', __name__)
student_model = Student(db)
project_model = Project(db)
skill_model = Skill(db)

@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    try:
        user_id = get_jwt_identity()
        
        # Get profile info
        profile = student_model.get_profile(user_id)
        
        # Get counts
        project_count = project_model.get_project_count(user_id)
        skills = skill_model.get_skills(user_id)
        skill_count = len(skills)
        
        # Get skill level distribution
        skill_levels = {'beginner': 0, 'intermediate': 0, 'advanced': 0, 'expert': 0}
        for skill in skills:
            level = skill.get('level', 'beginner')
            if level in skill_levels:
                skill_levels[level] += 1
        
        # Get recent projects (last 3)
        recent_projects = project_model.get_projects(user_id)[:3]
        for proj in recent_projects:
            proj['_id'] = str(proj['_id'])
            proj['id'] = str(proj['_id'])
        
        dashboard_data = {
            'profile': {
                'name': profile.get('name', '') if profile else '',
                'email': profile.get('email', '') if profile else ''
            },
            'stats': {
                'total_projects': project_count,
                'total_skills': skill_count,
                'skill_levels': skill_levels
            },
            'recent_projects': recent_projects
        }
        
        return jsonify(dashboard_data), 200
    except Exception as e:
        return {'message': f'Error fetching dashboard data: {str(e)}'}, 500