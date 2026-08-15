from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3

db = SQLAlchemy()

class Project(db.Model):
    """Project model for storing portfolio items"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    full_description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # web, data, automation, api, game, desktop
    technologies = db.Column(db.String(200), nullable=False)
    github_link = db.Column(db.String(200), nullable=True)
    demo_link = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(100), nullable=True, default='default-project.jpg')
    code_snippet = db.Column(db.Text, nullable=True)  # Store your Python code
    code_output = db.Column(db.Text, nullable=True)   # Store the output
    demo_note = db.Column(db.Text, nullable=True)     # explains how the Run Code demo relates to the real project
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Project {self.title}>'

class CodeExecution(db.Model):
    """Store code execution history"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    code = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)