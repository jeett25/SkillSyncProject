from datetime import datetime
from bson import ObjectId

class Resume:
    def __init__(self, db):
        self.collection = db['resumes']

    def add_resume(self, data):
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        return self.collection.insert_one(data)

    def get_resume_by_user(self, user_id):
        return self.collection.find_one({'user_id': user_id})

    def update_resume(self, user_id, data):
        data['updated_at'] = datetime.utcnow()
        return self.collection.update_one(
            {'user_id': user_id}, 
            {'$set': data}
        )

    def delete_resume(self, user_id):
        return self.collection.delete_one({'user_id': user_id})

    def mark_as_parsed(self, user_id, extracted_data):
        update_data = {
            'parsed': True,
            'extracted_text': extracted_data.get('text', ''),
            'extracted_skills': extracted_data.get('skills', []),
            'extracted_experience': extracted_data.get('experience', []),
            'extracted_education': extracted_data.get('education', []),
            'parsed_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        return self.collection.update_one(
            {'user_id': user_id},
            {'$set': update_data}
        )

    def get_all_resumes(self):
        return list(self.collection.find().sort('upload_date', -1))

    def get_unparsed_resumes(self):
        return list(self.collection.find({'parsed': False}).sort('upload_date', -1))

    def get_resume_stats(self):
        total_resumes = self.collection.count_documents({})
        parsed_resumes = self.collection.count_documents({'parsed': True})
        unparsed_resumes = self.collection.count_documents({'parsed': False})
        
        # Get most common skills from parsed resumes
        pipeline = [
            {'$match': {'parsed': True}},
            {'$unwind': '$extracted_skills'},
            {'$group': {
                '_id': '$extracted_skills',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        
        top_skills = list(self.collection.aggregate(pipeline))
        
        return {
            'total_resumes': total_resumes,
            'parsed_resumes': parsed_resumes,
            'unparsed_resumes': unparsed_resumes,
            'top_skills': top_skills
        }