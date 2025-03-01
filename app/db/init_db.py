from app.db.session import engine, Base
from app.db.models.task import Task

def init_db():
    '''Create database tables from SQLAlchemy models.'''
    Base.metadata.create_all(bind=engine)