"""
Shared SQLAlchemy Base Class
All ORM models inherit from this single base
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
