from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models.resume_upload import Resume
from app.utils.resume_parser import ResumeParser
from app import db
import os
import uuid
from datetime import datetime

resume_bp = Blueprint('resume', __name__)

# Configure upload settings
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file):
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)     # Seek back to beginning
    return size

@resume_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_resume():
    try:
        user_id = get_jwt_identity()
        
        # Check if file is present
        if 'resume' not in request.files:
            return {'message': 'No file provided'}, 400
        
        file = request.files['resume']
        
        # Check if file is selected
        if file.filename == '':
            return {'message': 'No file selected'}, 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return {'message': 'File type not allowed. Please upload PDF, DOC, or DOCX files'}, 400
        
        # Check file size
        if get_file_size(file) > MAX_FILE_SIZE:
            return {'message': 'File size too large. Maximum size is 5MB'}, 400
        
        # Create uploads directory if it doesn't exist
        upload_folder = os.path.join(current_app.root_path, 'uploads', 'resumes')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{user_id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Initialize resume model
        resume_model = Resume(db)
        
        # Check if user already has a resume
        existing_resume = resume_model.get_resume_by_user(user_id)
        
        resume_data = {
            'user_id': user_id,
            'original_filename': file.filename,
            'stored_filename': unique_filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'file_type': file_extension,
            'upload_date': datetime.utcnow(),
            'parsed': False,
            'extracted_skills': [],
            'extracted_text': ''
        }
        
        if existing_resume:
            # Delete old file if it exists
            if os.path.exists(existing_resume['file_path']):
                os.remove(existing_resume['file_path'])
            
            # Update existing resume record
            result = resume_model.update_resume(user_id, resume_data)
            message = 'Resume updated successfully'
        else:
            # Create new resume record
            result = resume_model.add_resume(resume_data)
            message = 'Resume uploaded successfully'
        
        # Return success response
        return {
            'message': message,
            'filename': file.filename,
            'file_size': resume_data['file_size']
        }, 201
        
    except Exception as e:
        print(f"Error in upload_resume: {str(e)}")
        return {'message': f'Error uploading resume: {str(e)}'}, 500

@resume_bp.route('/info', methods=['GET'])
@jwt_required()
def get_resume_info():
    try:
        user_id = get_jwt_identity()
        resume_model = Resume(db)
        
        resume = resume_model.get_resume_by_user(user_id)
        
        if not resume:
            return {'message': 'No resume found'}, 404
        
        # Convert ObjectId to string
        resume['_id'] = str(resume['_id'])
        
        # Remove sensitive file path info
        resume_info = {
            '_id': resume['_id'],
            'original_filename': resume['original_filename'],
            'file_size': resume['file_size'],
            'file_type': resume['file_type'],
            'upload_date': resume['upload_date'],
            'parsed': resume['parsed'],
            'extracted_skills': resume.get('extracted_skills', [])
        }
        
        return jsonify(resume_info), 200
        
    except Exception as e:
        print(f"Error in get_resume_info: {str(e)}")
        return {'message': f'Error fetching resume info: {str(e)}'}, 500

@resume_bp.route('/parse', methods=['POST'])
@jwt_required()
def parse_resume():
    try:
        user_id = get_jwt_identity()
        resume_model = Resume(db)
        
        # Get user's resume
        resume = resume_model.get_resume_by_user(user_id)
        
        if not resume:
            return {'message': 'No resume found. Please upload a resume first.'}, 404
        
        if resume.get('parsed', False):
            return {'message': 'Resume already parsed'}, 400
        
        # Initialize parser
        parser = ResumeParser()
        
        # Parse the resume
        parsed_data = parser.parse_resume(resume['file_path'], resume['file_type'])
        
        if 'error' in parsed_data:
            return {'message': parsed_data['error']}, 500
        
        # Save parsed data to database
        result = resume_model.mark_as_parsed(user_id, parsed_data)
        
        if result.modified_count > 0:
            return {
                'message': 'Resume parsed successfully',
                'extracted_skills': parsed_data.get('skills', []),
                'skills_count': len(parsed_data.get('skills', [])),
                'word_count': parsed_data.get('word_count', 0)
            }, 200
        else:
            return {'message': 'Failed to save parsed data'}, 500
            
    except Exception as e:
        print(f"Error in parse_resume: {str(e)}")
        return {'message': f'Error parsing resume: {str(e)}'}, 500

@resume_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_resume():
    try:
        user_id = get_jwt_identity()
        resume_model = Resume(db)
        
        # Get resume info first
        resume = resume_model.get_resume_by_user(user_id)
        
        if not resume:
            return {'message': 'No resume found'}, 404
        
        # Delete file from filesystem
        if os.path.exists(resume['file_path']):
            os.remove(resume['file_path'])
        
        # Delete from database
        result = resume_model.delete_resume(user_id)
        
        if result.deleted_count > 0:
            return {'message': 'Resume deleted successfully'}, 200
        else:
            return {'message': 'Failed to delete resume'}, 500
            
    except Exception as e:
        print(f"Error in delete_resume: {str(e)}")
        return {'message': f'Error deleting resume: {str(e)}'}, 500