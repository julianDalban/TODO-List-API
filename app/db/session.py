from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'sqlite:///./app.db' # Tell SQLAlchemy where to find the db, '///.' means curr directory

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False} # This argument is for SQLite - allows multiple threads to interact with the database, important for web apps
)

# Session Factory 
# Session is main interface for db operations
# SessionLocal is a class that produces new session object when called
SessionLocal = sessionmaker(
    autocommit=False, # when False, changes are accumulated and applied at once when session.commit() is called
    autoflush=False, # when False, SQLAlchemy doesn't auto flush before every query (sending SQL to the database but not comitting it)
    bind=engine # engine tells the session how to connect to the db
)

# create base class for our models, all our db models will inherit from this base class
# SQLAlchemy uses this to map classes to db tables
Base = declarative_base()

# Dependency function for FastAPI
def get_db():
    '''
    Creates a new db session for each request and automatically closes it when the request is finished.
    In FastAPI, this function will be used as a dependency:
    
    @app.get('/items/')
    def read_items(db: Session = Depends(get_db)):
        # use db session
    '''
    db = SessionLocal()
    try:
        yield db # Suspends the function and returns the db session. when route function finishes, execution resumes here
    finally:
        db.close() # Ensures session is closed even in case of exception