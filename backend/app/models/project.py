from datetime import datetime, timedelta
from bson import ObjectId

class Project:
    def __init__(self, db):
        self.collection = db['projects']

    def add_project(self, data):
        """Add a new project"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        return self.collection.insert_one(data)

    def get_projects(self, user_id):
        """Get all projects for a user"""
        return list(self.collection.find({'user_id': user_id}).sort('created_at', -1))

    def get_project_by_id(self, project_id, user_id):
        """Get a specific project by ID and user ID"""
        return self.collection.find_one({
            '_id': ObjectId(project_id),
            'user_id': user_id
        })

    def update_project(self, project_id, user_id, data):
        """Update a project"""
        data['updated_at'] = datetime.utcnow()
        return self.collection.update_one(
            {'_id': ObjectId(project_id), 'user_id': user_id},
            {'$set': data}
        )

    def delete_project(self, project_id, user_id):
        """Delete a project"""
        return self.collection.delete_one({
            '_id': ObjectId(project_id),
            'user_id': user_id
        })

    def get_project_count(self, user_id):
        """Get the count of projects for a user"""
        return self.collection.count_documents({'user_id': user_id})

    # Admin/Analytics methods
    def get_total_project_count(self):
        """Get total number of projects across all users"""
        return self.collection.count_documents({})

    def get_all_projects(self):
        """Get all projects (admin function)"""
        return list(self.collection.find().sort('created_at', -1))

    def get_recent_projects(self, limit=10):
        """Get recently created projects"""
        return list(self.collection.find().sort('created_at', -1).limit(limit))

    def get_project_creation_trends(self, months=6):
        """Get project creation trends for the last N months"""
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
        
        # Format results for frontend charts
        formatted_results = []
        for result in results:
            month_name = datetime(result['_id']['year'], result['_id']['month'], 1).strftime('%b %Y')
            formatted_results.append({
                'month': month_name,
                'projects': result['count']
            })
        
        return formatted_results

    def get_monthly_growth(self):
        """Get monthly project growth rate"""
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        current_month_projects = self.collection.count_documents({
            'created_at': {'$gte': current_month}
        })
        
        last_month_projects = self.collection.count_documents({
            'created_at': {'$gte': last_month, '$lt': current_month}
        })
        
        if last_month_projects == 0:
            return 100 if current_month_projects > 0 else 0
        
        growth_rate = ((current_month_projects - last_month_projects) / last_month_projects) * 100
        return round(growth_rate, 2)

    def get_project_categories(self):
        """Get project categories/types distribution"""
        pipeline = [
            {'$group': {
                '_id': '$category',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        
        return list(self.collection.aggregate(pipeline))

    def get_projects_by_technology(self):
        """Get projects grouped by technology stack"""
        pipeline = [
            {'$unwind': {'path': '$technologies', 'preserveNullAndEmptyArrays': True}},
            {'$group': {
                '_id': '$technologies',
                'count': {'$sum': 1}
            }},
            {'$match': {'_id': {'$ne': None}}},
            {'$sort': {'count': -1}},
            {'$limit': 20}
        ]
        
        return list(self.collection.aggregate(pipeline))

    def get_project_stats_by_user(self):
        """Get project statistics by user"""
        pipeline = [
            {'$group': {
                '_id': '$user_id',
                'project_count': {'$sum': 1},
                'latest_project': {'$max': '$created_at'}
            }},
            {'$sort': {'project_count': -1}},
            {'$limit': 10}
        ]
        
        return list(self.collection.aggregate(pipeline))

    def get_active_projects_last_30_days(self):
        """Get projects created in the last 30 days"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        return self.collection.count_documents({
            'created_at': {'$gte': thirty_days_ago}
        })

    def search_projects(self, query):
        """Search projects by title or description"""
        return list(self.collection.find({
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}}
            ]
        }))

    def get_project_completion_stats(self):
        """Get project completion statistics (if you have a status field)"""
        pipeline = [
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]
        
        return list(self.collection.aggregate(pipeline))