import sys
import os
# Add the project root directory to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.db.session import Base, get_db
import app.db.models.task

# Define the test database URL (using SQLite in-memory for speed and simplicity)
TEST_DATABASE_URL = 'sqlite:///:memory:?cache=shared'

# Create the test database engine
# we use chack_same_thread=False to allow SQLite to work with FastAPI's asynchronous nature
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={'check_same_thread': False}
)

# create a TestSessionLocal class for creating db sessions
TestSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=test_engine
)

@pytest.fixture(scope='session')
def setup_test_db():
    '''
    Setup fixture that creates all database tables at the beginning of testing
    and drops them after all tests are done.
    
    Scope='session' means this fixture runs once per test session
    '''
    print("\n=== SETUP DATABASE START ===")
    
    # Check if engine is properly configured
    print(f"Database URL: {TEST_DATABASE_URL}")
    print(f"Engine: {test_engine}")
    
    # Check what tables exist before creation
    inspector = inspect(test_engine)
    before_tables = inspector.get_table_names()
    print(f"Tables before creation: {before_tables}")
    
    # Create all tables
    try:
        Base.metadata.create_all(bind=test_engine)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise
    
    # Check what tables exist after creation
    inspector = inspect(test_engine)
    after_tables = inspector.get_table_names()
    print(f"Tables after creation: {after_tables}")
    
    yield
    
    # After all tests, drop the tables
    print("\n=== TEARDOWN DATABASE START ===")
    try:
        Base.metadata.drop_all(bind=test_engine)
        print("Tables dropped successfully")
    except Exception as e:
        print(f"Error dropping tables: {e}")
    
    print("=== TEARDOWN DATABASE END ===")

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
    # Use the existing engine with the shared cache
    connection = test_engine.connect()
    # start transaction
    transaction = connection.begin()
    
    # Create a new session for the test
    session = TestSessionLocal(bind=connection)
    
    try:
        # provide the session to the test
        yield session
    finally:
        # after test completes (even if it fails), rollback any changes
        transaction.rollback()
        # and close the session
        connection.close()

@pytest.fixture(scope='function')
def client(db_session):
    from app.main import app
    '''
    Fixture that creates a TestClient with a test database session.
    
    This fixture:
    1. Overrides the get_db dependency to use our test session
    2. Creates a TestClient with this override
    3. Yields the client for the test to use
    4. Resets the override after the test
    
    This allows tests to make API requests that use the test database.
    '''
    # Define a function that will replace get_db in our FastAPI app
    def override_get_db():
        try:
            yield db_session
        finally:
            pass # Cleanup is handled by the db_session fixture
        
    # override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # create and yield the test client
    with TestClient(app) as test_client:
        yield test_client

    # reset the dependency override after the test
    app.dependency_overrides = {}

@pytest.fixture(scope='function')
def sample_task(db_session):
    '''
    Fixture that creates a sample task in the db.
    
    This is useful for tests that need pre-existing data.
    '''
    from app.db.models.task import Task as TaskModel
    
    # create a task instance
    unique_id = str(uuid.uuid4())[:8]
    task = TaskModel(
        title=f'Test Task {unique_id}',
        description='This is a test task',
        status='pending',
        priority=3
    )
    
    # add it to the database
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    
    # return the created task to use in tests
    return task

# run all tests, the following command is: pytest -v
# run just repository tests: pytest tests/unit/test_repositories -v
# run just service tests: pytest tests/unit/test_services -v
# run just API tests: pytest tests/integration -v
# run a specific test file: pytest tests/unit/test_repositories/test_task_repository.py -v