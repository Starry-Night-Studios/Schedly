from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with courses
    courses = db.relationship('Course', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    room = db.Column(db.String(50), nullable=False)
    instructor = db.Column(db.String(100), nullable=False)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship with schedules
    schedules = db.relationship('Schedule', backref='course', lazy=True, cascade='all, delete-orphan')
    
    # Add composite unique constraint to prevent duplicate courses for same user
    __table_args__ = (db.UniqueConstraint('user_id', 'code', 'title', name='unique_user_course'),)
    
    def to_dict(self):
        return {
            'code': self.code,
            'title': self.title,
            'room': self.room,
            'instructor': self.instructor,
            'schedule': [schedule.to_dict() for schedule in self.schedules]
        }

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(10), nullable=False)
    start = db.Column(db.String(5), nullable=False)  # Format: HH:MM
    end = db.Column(db.String(5), nullable=False)    # Format: HH:MM
    
    # Foreign key to course
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Add unique constraint to prevent duplicate schedules for same course
    __table_args__ = (db.UniqueConstraint('course_id', 'day', 'start', 'end', name='unique_course_schedule'),)
    
    def to_dict(self):
        return {
            'day': self.day,
            'start': self.start,
            'end': self.end
        }