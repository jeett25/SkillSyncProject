from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.skill import Skill
from app import db
from bson import ObjectId

skills_bp = Blueprint('skills', __name__)
skill_model = Skill(db)

@skills_bp.route('/skills', methods=['POST'])
@jwt_required()
def add_skill():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('skill'):
            return {'message': 'Skill name is required'}, 400
        
        # Check if skill already exists
        existing_skill = skill_model.find_skill_by_name(user_id, data['skill'])
        if existing_skill:
            return {'message': 'Skill already exists'}, 400
        
        # Set default level if not provided
        if 'level' not in data:
            data['level'] = 'beginner'
        
        data['user_id'] = user_id
        result = skill_model.add_skill(data)
        
        return {
            'message': 'Skill added successfully',
            'skill_id': str(result.inserted_id)
        }, 201
    except Exception as e:
        return {'message': f'Error adding skill: {str(e)}'}, 500

@skills_bp.route('/skills', methods=['GET'])
@jwt_required()
def get_skills():
    try:
        user_id = get_jwt_identity()
        skills = skill_model.get_skills(user_id)
        
        # Convert ObjectId to string for JSON serialization
        for skill in skills:
            skill['_id'] = str(skill['_id'])
            skill['id'] = str(skill['_id'])  # Add id field for frontend
            
        return jsonify(skills), 200
    except Exception as e:
        return {'message': f'Error fetching skills: {str(e)}'}, 500

@skills_bp.route('/skills/<skill_id>', methods=['PUT'])
@jwt_required()
def update_skill(skill_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate ObjectId
        if not ObjectId.is_valid(skill_id):
            return {'message': 'Invalid skill ID'}, 400
        
        # Update skill
        result = skill_model.update_skill(skill_id, data)
        
        if result.matched_count == 0:
            return {'message': 'Skill not found'}, 404
        
        return {'message': 'Skill updated successfully'}, 200
    except Exception as e:
        return {'message': f'Error updating skill: {str(e)}'}, 500

@skills_bp.route('/skills/<skill_id>', methods=['DELETE'])
@jwt_required()
def delete_skill(skill_id):
    try:
        user_id = get_jwt_identity()
        
        # Validate ObjectId
        if not ObjectId.is_valid(skill_id):
            return {'message': 'Invalid skill ID'}, 400
        
        result = skill_model.delete_skill(skill_id)
        
        if result.deleted_count == 0:
            return {'message': 'Skill not found'}, 404
        
        return {'message': 'Skill deleted successfully'}, 200
    except Exception as e:
        return {'message': f'Error deleting skill: {str(e)}'}, 500

@skills_bp.route('/skills', methods=['DELETE'])
@jwt_required()
def delete_skill_by_name():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('skill'):
            return {'message': 'Skill name is required'}, 400
        
        result = skill_model.delete_skill_by_name(user_id, data['skill'])
        
        if result.deleted_count == 0:
            return {'message': 'Skill not found'}, 404
        
        return {'message': 'Skill deleted successfully'}, 200
    except Exception as e:
        return {'message': f'Error deleting skill: {str(e)}'}, 500