from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.project import Project
from app import db
from bson import ObjectId

project_bp = Blueprint('project', __name__)
project_model = Project(db)

@project_bp.route('/projects', methods=['POST'])
@jwt_required()
def add_project():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('description'):
            return {'message': 'Title and description are required'}, 400
        
        data['user_id'] = user_id
        result = project_model.add_project(data)
        
        return {
            'message': 'Project added successfully',
            'project_id': str(result.inserted_id)
        }, 201
    except Exception as e:
        return {'message': f'Error adding project: {str(e)}'}, 500

@project_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    try:
        user_id = get_jwt_identity()
        projects = project_model.get_projects(user_id)
        
        # Convert ObjectId to string for JSON serialization
        for proj in projects:
            proj['_id'] = str(proj['_id'])
            proj['id'] = str(proj['_id'])  # Add id field for frontend
            
        return jsonify(projects), 200
    except Exception as e:
        return {'message': f'Error fetching projects: {str(e)}'}, 500

@project_bp.route('/projects/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    try:
        user_id = get_jwt_identity()
        
        # Validate ObjectId
        if not ObjectId.is_valid(project_id):
            return {'message': 'Invalid project ID'}, 400
        
        project = project_model.get_project_by_id(project_id, user_id)
        
        if not project:
            return {'message': 'Project not found'}, 404
        
        project['_id'] = str(project['_id'])
        project['id'] = str(project['_id'])
        
        return jsonify(project), 200
    except Exception as e:
        return {'message': f'Error fetching project: {str(e)}'}, 500

@project_bp.route('/projects/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate ObjectId
        if not ObjectId.is_valid(project_id):
            return {'message': 'Invalid project ID'}, 400
        
        result = project_model.update_project(project_id, user_id, data)
        
        if result.matched_count == 0:
            return {'message': 'Project not found'}, 404
        
        return {'message': 'Project updated successfully'}, 200
    except Exception as e:
        return {'message': f'Error updating project: {str(e)}'}, 500

@project_bp.route('/projects/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    try:
        user_id = get_jwt_identity()
        
        # Validate ObjectId
        if not ObjectId.is_valid(project_id):
            return {'message': 'Invalid project ID'}, 400
        
        result = project_model.delete_project(project_id, user_id)
        
        if result.deleted_count == 0:
            return {'message': 'Project not found'}, 404
        
        return {'message': 'Project deleted successfully'}, 200
    except Exception as e:
        return {'message': f'Error deleting project: {str(e)}'}, 500