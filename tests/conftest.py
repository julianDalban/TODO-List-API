import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import Base, get_db

# Define the test database URL (using SQLite in-memory for speed and simplicity)
TEST_DATABASE_URL = 'sqlite:///./test.db'

# Create the test database engine
# we use chack_same_thread=False to allow SQLite to work with FastAPI's asynchronous nature
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={'check_same_thread': False}
)

# create a TestSessionLocal class for creating db sessions
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope='session')
def setup_test_db():
    '''
    Setup fixture that creates all database tables at the beginning of testing
    and drops them after all tests are done.
    
    Scope='session' means this fixture runs once per test session
    '''
    # Create all tables defined in our SQLAlchemy models
    Base.metadata.create_all(bind=test_engine)
    
    # Run all the tests
    yield
    
    # After all tests, drop the tables
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope='function')
def db_session(setup_test_db):
    '''
    Fixture that creates a new database session for a test function.
    
    The scope='function' means this fixture runs for each test function.
    
    This fixture:
    1. Creates a new db session.
    2. Yields that session to the test
    3. Rolls back any changes after the test completes
    4. Closes the session
    
    This ensures test isolation - changes from one test don't affect others.
    '''