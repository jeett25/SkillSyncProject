from datetime import datetime, timedelta
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import logging

class User:
    def __init__(self, db):
        self.collection = db['users']

    def create_user(self, data):
        """Create a new user"""
        # Hash password using Werkzeug
        hashed_password = generate_password_hash(data['password'])
        
        user_data = {
            'email': data['email'],
            'password': hashed_password,
            'role': data.get('role', 'user'),  # Default role is 'user'
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True
        }
        
        return self.collection.insert_one(user_data)

    def find_by_email(self, email):
        """Find user by email"""
        return self.collection.find_one({'email': email})

    def find_by_id(self, user_id):
        """Find user by ID"""
        return self.collection.find_one({'_id': ObjectId(user_id)})

    def check_password(self, hashed_pw, plain_pw):
        """Check if password matches with error handling"""
        try:
            # Check if hashed_pw is None or empty
            if not hashed_pw:
                logging.warning("Hashed password is None or empty")
                return False
            
            # Check if plain_pw is None or empty
            if not plain_pw:
                logging.warning("Plain password is None or empty")
                return False
            
            return check_password_hash(hashed_pw, plain_pw)
            
        except Exception as e:
            logging.error(f"Error in check_password: {e}")
            return False

    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        return self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'last_login': datetime.utcnow()}}
        )

    def get_user_count(self):
        """Get total number of users"""
        return self.collection.count_documents({})

    def get_all_users(self):
        """Get all users (admin function)"""
        return list(self.collection.find().sort('created_at', -1))

    def get_recent_users(self, limit=10):
        """Get recently registered users"""
        return list(self.collection.find().sort('created_at', -1).limit(limit))

    def get_user_registration_trends(self, months=6):
        """Get user registration trends for the last N months"""
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
                'users': result['count']
            })
        
        return formatted_results

    def get_monthly_growth(self):
        """Get monthly growth rate"""
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        current_month_users = self.collection.count_documents({
            'created_at': {'$gte': current_month}
        })
        
        last_month_users = self.collection.count_documents({
            'created_at': {'$gte': last_month, '$lt': current_month}
        })
        
        if last_month_users == 0:
            return 100 if current_month_users > 0 else 0
        
        growth_rate = ((current_month_users - last_month_users) / last_month_users) * 100
        return round(growth_rate, 2)

    def update_user_role(self, user_id, role):
        """Update user role (admin function)"""
        return self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'role': role, 'updated_at': datetime.utcnow()}}
        )

    def deactivate_user(self, user_id):
        """Deactivate user account"""
        return self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )

    def activate_user(self, user_id):
        """Activate user account"""
        return self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_active': True, 'updated_at': datetime.utcnow()}}
        )

    def get_active_users_count(self):
        """Get count of active users"""
        return self.collection.count_documents({'is_active': True})

    def get_users_by_role(self, role):
        """Get users by role"""
        return list(self.collection.find({'role': role}))

    def search_users(self, query):
        """Search users by email"""
        return list(self.collection.find({
            'email': {'$regex': query, '$options': 'i'}
        }))

    def get_user_activity_stats(self):
        """Get user activity statistics"""
        total_users = self.get_user_count()
        active_users = self.get_active_users_count()
        
        # Users who logged in within last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_active = self.collection.count_documents({
            'last_login': {'$gte': thirty_days_ago}
        })
        
        # Users who never logged in
        never_logged_in = self.collection.count_documents({
            'last_login': None
        })
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'recent_active': recent_active,
            'never_logged_in': never_logged_in,
            'inactive_users': total_users - active_users
        }

    def update_password(self, user_id, new_password):
        """Update user password"""
        hashed_password = generate_password_hash(new_password)
        return self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password': hashed_password, 'updated_at': datetime.utcnow()}}
        )

    def migrate_plain_text_passwords(self):
        """
        Migration utility to hash plain text passwords in existing database
        WARNING: Only run this once for migration purposes
        """
        # Find users with potentially plain text passwords
        # Werkzeug hashes typically start with 'pbkdf2:sha256:' or 'scrypt:'
        users_with_plain_passwords = self.collection.find({
            'password': {'$not': {'$regex': r'^(pbkdf2:|scrypt:|argon2:)'}}
        })
        
        updated_count = 0
        for user in users_with_plain_passwords:
            if 'password' in user and user['password']:
                # Hash the plain text password
                hashed_password = generate_password_hash(user['password'])
                
                # Update in database
                self.collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {
                        'password': hashed_password,
                        'updated_at': datetime.utcnow()
                    }}
                )
                updated_count += 1
        
        return updated_count