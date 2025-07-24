from models import db, User, Course, Schedule

def save_user(email, schedule_data):
    """Save user email and schedule to database"""
    try:
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Delete existing courses for this user ONLY
            Course.query.filter_by(user_id=user.id).delete()
            db.session.flush()  # Ensure deletion is committed before adding new data
        else:
            # Create new user
            user = User(email=email)
            db.session.add(user)
            db.session.flush()  # Get user.id immediately
        
        # Add courses and schedules for THIS SPECIFIC USER
        for course_data in schedule_data:
            # Create course specifically for this user
            course = Course(
                code=course_data['code'],
                title=course_data['title'],
                room=course_data['room'],
                instructor=course_data['instructor'],
                user_id=user.id  # This ensures the course belongs to THIS user
            )
            db.session.add(course)
            db.session.flush()  # Get course.id immediately
            
            # Add schedules for this specific course
            for schedule_item in course_data['schedule']:
                schedule = Schedule(
                    day=schedule_item['day'],
                    start=schedule_item['start'],
                    end=schedule_item['end'],
                    course_id=course.id  # This links to the course for THIS user
                )
                db.session.add(schedule)
        
        # Commit all changes at once
        db.session.commit()
        print(f"User {email} saved successfully to database")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving user: {e}")
        raise

def get_all_users():
    """Get all users from database"""
    try:
        users = User.query.all()
        result = []
        
        for user in users:
            user_data = {
                "email": user.email,
                "schedule": [course.to_dict() for course in user.courses]
            }
            result.append(user_data)
        
        return result
    except Exception as e:
        print(f"Error reading users: {e}")
        return []

def get_user_schedule(email):
    """Get specific user's schedule"""
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            return [course.to_dict() for course in user.courses]
        return []
    except Exception as e:
        print(f"Error getting user schedule: {e}")
        return []

def debug_user_data(email):
    """Debug function to check user's data"""
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User: {user.email} (ID: {user.id})")
            for course in user.courses:
                print(f"  Course: {course.code} (ID: {course.id}, User ID: {course.user_id})")
                for schedule in course.schedules:
                    print(f"    Schedule: {schedule.day} {schedule.start}-{schedule.end} (Course ID: {schedule.course_id})")
        else:
            print(f"User {email} not found")
    except Exception as e:
        print(f"Error debugging user data: {e}")