from datetime import datetime, timedelta
from bson import ObjectId

class Skill:
    def __init__(self, db):
        self.collection = db['skills']

    def add_skill(self, data):
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        return self.collection.insert_one(data)

    def get_skills(self, user_id):
        return list(self.collection.find({'user_id': user_id}).sort('created_at', -1))

    def update_skill(self, skill_id, data):
        data['updated_at'] = datetime.utcnow()
        return self.collection.update_one(
            {'_id': ObjectId(skill_id)}, 
            {'$set': data}
        )

    def delete_skill(self, skill_id):
        return self.collection.delete_one({'_id': ObjectId(skill_id)})

    def delete_skill_by_name(self, user_id, skill_name):
        return self.collection.delete_one({
            'user_id': user_id, 
            'skill': skill_name
        })

    def find_skill_by_name(self, user_id, skill_name):
        return self.collection.find_one({
            'user_id': user_id, 
            'skill': skill_name
        })
    
    def get_skill_by_id(self, skill_id, user_id):
        """Get a specific skill by ID and user ID"""
        return self.collection.find_one({
            '_id': ObjectId(skill_id),
            'user_id': user_id
        })
    
    def get_skill_count(self, user_id):
        """Get the count of skills for a user"""
        return self.collection.count_documents({'user_id': user_id})
    def get_skill_count(self, user_id):
        """Get the count of skills for a user"""
        return self.collection.count_documents({'user_id': user_id})

    # Analytics methods for admin dashboard
    def get_total_skill_count(self):
        """Get total number of skills across all users"""
        return self.collection.count_documents({})

    def get_skill_level_distribution(self):
        """Get distribution of skill levels"""
        pipeline = [
            {'$group': {
                '_id': '$level',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        # Format for frontend
        distribution = {'beginner': 0, 'intermediate': 0, 'advanced': 0, 'expert': 0}
        for result in results:
            level = result['_id'] or 'beginner'
            if level in distribution:
                distribution[level] = result['count']
        
        return distribution

    def get_popular_skills(self, limit=20):
        """Get most popular skills across all users"""
        pipeline = [
            {'$group': {
                '_id': '$skill',
                'count': {'$sum': 1},
                'avg_level': {'$avg': {
                    '$switch': {
                        'branches': [
                            {'case': {'$eq': ['$level', 'beginner']}, 'then': 1},
                            {'case': {'$eq': ['$level', 'intermediate']}, 'then': 2},
                            {'case': {'$eq': ['$level', 'advanced']}, 'then': 3},
                            {'case': {'$eq': ['$level', 'expert']}, 'then': 4}
                        ],
                        'default': 1
                    }
                }}
            }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]
        
        return list(self.collection.aggregate(pipeline))

    def get_skill_trends(self, months=6):
        """Get skill addition trends over time"""
        start_date = datetime.utcnow() - timedelta(days=30 * months)
        
        pipeline = [
            {'$match': {'created_at': {'$gte': start_date}}},
            {'$group': {
                '_id': {
                    'year': {'$year': '$created_at'},
                    'month': {'$month': '$created_at'}
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.year': 1, '_id.month': 1}}
        ]
        
        results = list(self.collection.aggregate(pipeline))
        
        # Format results
        formatted_results = []
        for result in results:
            month_name = datetime(result['_id']['year'], result['_id']['month'], 1).strftime('%b %Y')
            formatted_results.append({
                'month': month_name,
                'skills': result['count']
            })
        
        return formatted_results

    def get_skill_usage_stats(self):
        """Get comprehensive skill usage statistics"""
        total_skills = self.get_total_skill_count()
        unique_skills = len(self.get_unique_skills())
        
        return {
            'total_skills': total_skills,
            'unique_skills': unique_skills,
            'level_distribution': self.get_skill_level_distribution(),
            'popular_skills': self.get_popular_skills(10)
        }

    def get_unique_skills(self):
        """Get list of unique skill names"""
        return self.collection.distinct('skill')

    def get_adoption_rate(self):
        """Get skill adoption rate (new skills added this month vs last month)"""
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        current_month_skills = self.collection.count_documents({
            'created_at': {'$gte': current_month}
        })
        
        last_month_skills = self.collection.count_documents({
            'created_at': {'$gte': last_month, '$lt': current_month}
        })
        
        if last_month_skills == 0:
            return 100 if current_month_skills > 0 else 0
        
        adoption_rate = ((current_month_skills - last_month_skills) / last_month_skills) * 100
        return round(adoption_rate, 2)

    def get_skills_by_category(self):
        """Get skills grouped by category (if you have categories)"""
        # This would work if you add a 'category' field to skills
        pipeline = [
            {'$group': {
                '_id': '$category',
                'skills': {'$push': '$skill'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        
        return list(self.collection.aggregate(pipeline))

    def get_user_skill_distribution(self):
        """Get distribution of how many skills users have"""
        pipeline = [
            {'$group': {
                '_id': '$user_id',
                'skill_count': {'$sum': 1}
            }},
            {'$group': {
                '_id': '$skill_count',
                'user_count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        return list(self.collection.aggregate(pipeline))