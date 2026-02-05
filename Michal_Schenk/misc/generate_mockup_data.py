import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import random
from db_handling import UserModel, GameSessionModel, generate_password_hash, insert_row


def generate_mockup_data(num_users: int = 10, sessions_per_user: int = 5):
    """
    Fill gradproj.db with randomized test data.
    
    Args:
        num_users: Number of random users to generate
        sessions_per_user: Average number of game sessions per user
    """
    
    # First names and last names for generating realistic usernames
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", 
                    "Iris", "Jack", "Karen", "Leo", "Maya", "Nathan", "Olivia", "Peter"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", 
                    "Davis", "Rodriguez", "Martinez", "Wilson", "Anderson", "Taylor", "Thomas"]
    
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "example.com"]
    
    print(f"Generating {num_users} random users...")
    users = []
    
    for i in range(num_users):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate unique username
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@{random.choice(domains)}"
        
        # Create user with random creation date within last year
        created_at = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 365))
        
        user_data = {
            'username': username,
            'email': email,
            'created_at': created_at,
            'password_hash': generate_password_hash('testpass123')
        }
        
        try:
            user = insert_row(UserModel, user_data)
            users.append(user)
            print(f"  Created user: {username}")
        except Exception as e:
            print(f"  Error creating user {username}: {e}")
    
    print(f"\nGenerating game sessions ({sessions_per_user} per user on average)...")
    session_count = 0
    
    for user in users:
        # Random number of sessions for this user (±50% variation)
        num_sessions = random.randint(max(1, sessions_per_user // 2), sessions_per_user + sessions_per_user // 2)
        
        for j in range(num_sessions):
            # Random start date for session (before now, after user creation)
            days_ago = random.randint(0, (datetime.datetime.now() - user.created_at).days)
            started_at = datetime.datetime.now() - datetime.timedelta(days=days_ago, hours=random.randint(0, 23))
            
            # Random game stats
            score = random.randint(0, 10000)
            level_reached = random.randint(1, 50)
            
            session_data = {
                'user_id': user.id,
                'started_at': started_at,
                'score': score,
                'level_reached': level_reached
            }
            
            try:
                insert_row(GameSessionModel, session_data)
                session_count += 1
            except Exception as e:
                print(f"  Error creating session for user {user.username}: {e}")
    
    print(f"  Created {session_count} game sessions")
    print(f"\nMockup data generation complete!")
    print(f"  Total users: {len(users)}")
    print(f"  Total sessions: {session_count}")


if __name__ == '__main__':
    generate_mockup_data(num_users=15, sessions_per_user=8)
