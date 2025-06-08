from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.student import Student
from app import db  # Import the global db directly

student_bp = Blueprint('student', __name__)

@student_bp.route('/profile', methods=['POST'])
@jwt_required()
def add_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return {'message': 'No data provided'}, 400
        
        # Initialize student model with global db
        student_model = Student(db)
        
        # Check if profile already exists
        existing_profile = student_model.get_profile(user_id)
        if existing_profile:
            return {'message': 'Profile already exists. Use PUT to update.'}, 400
        
        data['user_id'] = user_id
        result = student_model.add_profile(data)
        
        if result.inserted_id:
            return {'message': 'Profile created successfully'}, 201
        else:
            return {'message': 'Failed to create profile'}, 500
            
    except Exception as e:
        print(f"Error in add_profile: {str(e)}")
        return {'message': f'Error creating profile: {str(e)}'}, 500

@student_bp.route('/profile', methods=['GET'])
@jwt_required()
def view_profile():
    try:
        user_id = get_jwt_identity()
        
        # Initialize student model with global db
        student_model = Student(db)
        profile = student_model.get_profile(user_id)
            
        if not profile:
            return jsonify({
                'name': '',
                'email': '',
                'about': '',
                'phone': '',
                'location': '',
                'github': '',
                'linkedin': '',
                'user_id': user_id
            }), 200
        
        # Convert ObjectId to string
        profile['_id'] = str(profile['_id'])
        return jsonify(profile), 200
        
    except Exception as e:
        print(f"Error in view_profile: {str(e)}")
        return {'message': f'Error fetching profile: {str(e)}'}, 500

@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
def edit_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return {'message': 'No data provided'}, 400
        
        print(f"=== PROFILE UPDATE DEBUG ===")
        print(f"User ID from JWT: {user_id}")
        print(f"Data received: {data}")
        print(f"Data type: {type(data)}")
        
        # Initialize student model with global db
        student_model = Student(db)
        
        # Check if user exists in database first
        existing_profile = student_model.get_profile(user_id)
        print(f"Existing profile found: {existing_profile is not None}")
        if existing_profile:
            print(f"Existing profile data: {existing_profile}")
        
        # Remove user_id from data if it exists (security)
        data.pop('user_id', None)
        data.pop('_id', None)  # Remove _id if it exists
        
        print(f"Data after cleanup: {data}")
        
        # Test database connection
        try:
            collections = db.list_collection_names()
            print(f"Available collections: {collections}")
            students_count = db.students.count_documents({})
            print(f"Total students in DB: {students_count}")
            
            # Check what users exist in students collection
            all_students = list(db.students.find({}, {"user_id": 1, "email": 1}))
            print(f"All students in DB: {all_students}")
            
        except Exception as db_error:
            print(f"Database connection error: {db_error}")
        
        result = student_model.update_profile(user_id, data)
        
        print(f"Update result: matched={result.matched_count}, modified={result.modified_count}")
        
        if result.matched_count == 0:
            print("No matching document found, creating new profile...")
            # Profile doesn't exist, create it
            data['user_id'] = user_id
            insert_result = student_model.add_profile(data)
            print(f"Insert result: {insert_result.inserted_id}")
            if insert_result.inserted_id:
                return {'message': 'Profile created successfully'}, 201
            else:
                return {'message': 'Failed to create profile'}, 500
        
        # Verify the update worked
        updated_profile = student_model.get_profile(user_id)
        print(f"Profile after update: {updated_profile}")
        
        return {'message': 'Profile updated successfully'}, 200
            
    except Exception as e:
        print(f"Error in edit_profile: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return {'message': f'Error updating profile: {str(e)}'}, 500