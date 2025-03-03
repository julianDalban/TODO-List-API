from sqlalchemy import Column, Integer, String, Text, func
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app.db.session import Base
from app.schemas.task import TaskStatus, TaskPriority

class Task(Base):
    '''SQLAlchemy model for the tasks table.'''
    __tablename__ = 'tasks'
    
    # Primary key with auto-incrementing ID
    id = Column(Integer, primary_key=True, index=True) 
    
    # Task title, unique and indexed for faster lookups
    title = Column(String(50), unique=True, index=True, nullable=False) 
    
    #Task description
    description = Column(Text, nullable=False)
    
    
    # Status stored as a string (enum val necessary)
    status = Column(
        String,
        nullable=False,
        default=TaskStatus.PENDING.value
    )
    
    # Priority stored as an int
    priority = Column(
        Integer,
        nullable=False,
        default=TaskPriority.VERY_LOW.value
    )
    
    # Timestamps for record-keeping
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )