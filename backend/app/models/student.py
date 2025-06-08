from datetime import datetime
from bson import ObjectId

class Student:
    def __init__(self, db):
        self.collection = db['students']

    def add_profile(self, data):
        """Add a new student profile"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        return self.collection.insert_one(data)

    def get_profile(self, user_id):
        """Get student profile by user ID"""
        return self.collection.find_one({'user_id': user_id})

    def update_profile(self, user_id, data):
        """Update student profile"""
        data['updated_at'] = datetime.utcnow()
        return self.collection.update_one(
            {'user_id': user_id}, 
            {'$set': data}
        )

    def delete_profile(self, user_id):
        """Delete student profile"""
        return self.collection.delete_one({'user_id': user_id})

    # Analytics methods for admin dashboard
    def get_student_count(self):
        """Get total number of student profiles"""
        return self.collection.count_documents({})

    def get_all_students(self):
        """Get all student profiles (admin function)"""
        return list(self.collection.find().sort('created_at', -1))

    def get_recent_students(self, limit=10):
        """Get recently created student profiles"""
        return list(self.collection.find().sort('created_at', -1).limit(limit))

    def get_students_by_location(self):
        """Get students grouped by location"""
        pipeline = [
            {'$match': {'location': {'$exists': True, '$ne': ''}}},
            {'$group': {
                '_id': '$location',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 20}
        ]
        
        return list(self.collection.aggregate(pipeline))

    def get_profile_completion_stats(self):
        """Get profile completion statistics"""
        # Define required fields for a complete profile
        required_fields = ['name', 'email', 'about', 'phone', 'location']
        
        total_profiles = self.get_student_count()
        
        # Count profiles with all required fields
        complete_profiles = self.collection.count_documents({
            field: {'$exists': True, '$ne': ''} for field in required_fields
        })
        
        # Count profiles with social links
        profiles_with_github = self.collection.count_documents({
            'github': {'$exists': True, '$ne': ''}
        })
        
        profiles_with_linkedin = self.collection.count_documents({
            'linkedin': {'$exists': True, '$ne': ''}
        })
        
        return {
            'total_profiles': total_profiles,
            'complete_profiles': complete_profiles,
            'completion_rate': round((complete_profiles / total_profiles * 100), 2) if total_profiles > 0 else 0,
            'profiles_with_github': profiles_with_github,
            'profiles_with_linkedin': profiles_with_linkedin,
            'github_adoption': round((profiles_with_github / total_profiles * 100), 2) if total_profiles > 0 else 0,
            'linkedin_adoption': round((profiles_with_linkedin / total_profiles * 100), 2) if total_profiles > 0 else 0
        }

    def search_students(self, query):
        """Search students by name, email, or location"""
        return list(self.collection.find({
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'email': {'$regex': query, '$options': 'i'}},
                {'location': {'$regex': query, '$options': 'i'}}
            ]
        }))

    def get_students_with_incomplete_profiles(self):
        """Get students with incomplete profiles"""
        required_fields = ['name', 'email', 'about', 'phone', 'location']
        
        # Find profiles missing any required field
        incomplete_profiles = []
        for field in required_fields:
            profiles = list(self.collection.find({
                '$or': [
                    {field: {'$exists': False}},
                    {field: ''}
                ]
            }))
            incomplete_profiles.extend(profiles)
        
        # Remove duplicates
        seen_ids = set()
        unique_incomplete = []
        for profile in incomplete_profiles:
            if profile['_id'] not in seen_ids:
                seen_ids.add(profile['_id'])
                unique_incomplete.append(profile)
        
        return unique_incomplete

    def get_social_media_stats(self):
        """Get social media presence statistics"""
        total_students = self.get_student_count()
        
        github_stats = self.collection.count_documents({
            'github': {'$exists': True, '$ne': ''}
        })
        
        linkedin_stats = self.collection.count_documents({
            'linkedin': {'$exists': True, '$ne': ''}
        })
        
        both_platforms = self.collection.count_documents({
            'github': {'$exists': True, '$ne': ''},
            'linkedin': {'$exists': True, '$ne': ''}
        })
        
        return {
            'total_students': total_students,
            'with_github': github_stats,
            'with_linkedin': linkedin_stats,
            'with_both': both_platforms,
            'github_percentage': round((github_stats / total_students * 100), 2) if total_students > 0 else 0,
            'linkedin_percentage': round((linkedin_stats / total_students * 100), 2) if total_students > 0 else 0,
            'both_percentage': round((both_platforms / total_students * 100), 2) if total_students > 0 else 0
        }