from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def generate_uuid():
    """Generate a UUID string for primary keys"""
    return str(uuid.uuid4())

