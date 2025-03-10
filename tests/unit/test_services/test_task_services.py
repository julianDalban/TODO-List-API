import pytest
from unittest.mock import MagicMock
from fastapi import status

from app.services.task_service import TaskService
from app.schemas.task import Task as TaskSchema, TaskStatus, TaskPriority
from app.schemas.pagination import SortField, SortOrder
from app.core.exceptions import CustomHTTPException

class TestTaskService:
    '''Test Suite for the TaskService class.'''
    
    def test_create_task_success(self, db_session):
        '''Test creating a task successfully.'''
        # Setup
        task_schema = TaskSchema(
            title='Service Test Task',
            description='Testing task creation in service',
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        service = TaskService(db_session)
        
        # Create a mock db model that would be returned by the repo
        mock_db_task = MagicMock()
        mock_db_task.title = task_schema.title
        mock_db_task.description = task_schema.description
        mock_db_task.status = task_schema.status
        mock_db_task.priority = task_schema.priority
        
        # We replace the repository interacting functions with predetermined vals (assume all went well on that layer)
        service.repository.get_by_title = MagicMock(return_value=None)
        service.repository.create = MagicMock(return_value=mock_db_task)
        
        # Test
        result = service.create_task(task_schema)
        
        # Verify
        assert result.title == task_schema.title
        assert result.description == task_schema.description
        assert result.status == task_schema.status
        assert result.priority == task_schema.priority
        
        # make sure the repo methods were called correctly
        service.repository.get_by_title.assert_called_once_with(task_schema.title)
        service.repository.create.assert_called_once_with(task_schema)
    
    def test_get_task_by_title_found(self, db_session):
        '''Test getting a task by title when it already exists'''
        # Setup
        service = TaskService(db_session)
        
        # mock db task
        mock_db_task = MagicMock()
        mock_db_task.title = 'Existing Task'
        mock_db_task.description = 'Test Description'
        mock_db_task.status = 'pending'
        mock_db_task.priority = 3
        
        service.repository.get_by_title = MagicMock(return_value=mock_db_task)
        
        # Test
        result = service.get_task_by_title('Existing Task')
        
        # Verify
        assert result is not None
        assert result.title == 'Existing Task'
        assert result.description == 'Test Description'
        assert result.status == 'pending'
        assert result.priority == 3
        service.repository.get_by_title.assert_called_once_with('Existing Task')
    
    def test_update_task_success(self, db_session):
        """Test successfully updating a task."""
        # setu-
        task_title = "Task to Update"
        task_update = TaskSchema(
            title=task_title,  # Title stays the same
            description="Updated description",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH
        )
        service = TaskService(db_session)
        
        # Create a mock updated DB task
        mock_db_task = MagicMock()
        mock_db_task.title = task_update.title
        mock_db_task.description = task_update.description
        mock_db_task.status = task_update.status
        mock_db_task.priority = task_update.priority
        
        service.repository.update = MagicMock(return_value=mock_db_task)
        
        # Test
        result = service.update_task(task_title, task_update)
        
        # Verify
        assert result.title == task_update.title
        assert result.description == task_update.description
        assert result.status == task_update.status
        assert result.priority == task_update.priority
        service.repository.update.assert_called_once_with(task_title, task_update)
    
    def test_get_task_by_title_not_found(self, db_session):
        '''Test getting a task by title when it doesn't exist.'''
        # Setup
        service = TaskService(db_session)
        # Configure the repository mock to return None (task not found)
        service.repository.get_by_title = MagicMock(return_value=None)
        
        # Test
        result = service.get_task_by_title('Non-existent Task')
        
        # Verify
        assert result is None
        service.repository.get_by_title.assert_called_once_with('Non-existent Task')

def test_create_task_duplicate(self, db_session):
    '''Test creating a task that already exists.'''
    # Setup
    task_schema = TaskSchema(
        title='Duplicate Task',
        description='Testing duplicate task creation',
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM
    )
    service = TaskService(db_session)
    
    # Mock existing task with same title
    existing_task = MagicMock()
    existing_task.title = task_schema.title
    service.repository.get_by_title = MagicMock(return_value=existing_task)
    
    # Test & Verify
    with pytest.raises(CustomHTTPException) as excinfo:
        service.create_task(task_schema)
    
    assert excinfo.value.status_code == status.HTTP_409_CONFLICT
    assert 'already exists' in excinfo.value.detail
    service.repository.get_by_title.assert_called_once_with(task_schema.title)

def test_update_task_title_mismatch(self, db_session):
    '''Test updating a task with mismatched titles.'''
    # Setup
    original_title = 'Original Title'
    task_update = TaskSchema(
        title='Different Title',  # Different title
        description='Updated description',
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH
    )
    service = TaskService(db_session)
    
    # Test & Verify
    with pytest.raises(CustomHTTPException) as excinfo:
        service.update_task(original_title, task_update)
    
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Cannot update a task name' in excinfo.value.detail

def test_update_task_not_found(self, db_session):
    '''Test updating a task that doesn't exist.'''
    # Setup
    task_title = 'Non-existent Task'
    task_update = TaskSchema(
        title=task_title,
        description='Updated description',
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.HIGH
    )
    service = TaskService(db_session)
    
    # Configure the repository mock to return None (task not found)
    service.repository.update = MagicMock(return_value=None)
    
    # Test & Verify
    with pytest.raises(CustomHTTPException) as excinfo:
        service.update_task(task_title, task_update)
    
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert 'Task does not exist' in excinfo.value.detail
    service.repository.update.assert_called_once_with(task_title, task_update)

def test_delete_task_success(self, db_session):
    '''Test deleting a task successfully.'''
    # Setup
    task_title = 'Task to Delete'
    service = TaskService(db_session)
    
    # Mock successful deletion
    service.repository.delete = MagicMock(return_value=True)
    
    # Test
    result = service.delete_task(task_title)
    
    # Verify
    assert result is True
    service.repository.delete.assert_called_once_with(task_title)

def test_delete_task_not_found(self, db_session):
    '''Test deleting a task that doesn't exist.'''
    # Setup
    task_title = 'Non-existent Task'
    service = TaskService(db_session)
    
    # Mock unsuccessful deletion (task not found)
    service.repository.delete = MagicMock(return_value=False)
    
    # Test & Verify
    with pytest.raises(CustomHTTPException) as excinfo:
        service.delete_task(task_title)
    
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert 'Task not found' in excinfo.value.detail
    service.repository.delete.assert_called_once_with(task_title)

def test_get_filtered_tasks(self, db_session):
    '''Test retrieving filtered tasks.'''
    # Setup
    service = TaskService(db_session)
    
    # Create mock DB tasks that would be returned by the repository
    mock_db_task1 = MagicMock()
    mock_db_task1.title = 'Task 1'
    mock_db_task1.description = 'Description 1'
    mock_db_task1.status = 'pending'
    mock_db_task1.priority = 3
    
    mock_db_task2 = MagicMock()
    mock_db_task2.title = 'Task 2'
    mock_db_task2.description = 'Description 2'
    mock_db_task2.status = 'completed'
    mock_db_task2.priority = 5
    
    # Mock repository's get_all to return our mock tasks
    service.repository.get_all = MagicMock(return_value=([mock_db_task1, mock_db_task2], 2))
    
    # Test
    status_filter = TaskStatus.PENDING
    priority_filter = TaskPriority.MEDIUM
    search_term = 'test'
    sort_by = SortField.TITLE
    sort_order = SortOrder.DESC
    skip = 0
    limit = 10
    
    result_tasks, result_count = service.get_filtered_tasks(
        status=status_filter,
        priority=priority_filter,
        search=search_term,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )
    
    # Verify
    assert len(result_tasks) == 2
    assert result_count == 2
    assert result_tasks[0].title == 'Task 1'
    assert result_tasks[1].title == 'Task 2'
    
    # Check that repository method was called with correct parameters
    service.repository.get_all.assert_called_once_with(
        status=status_filter.value,
        priority=priority_filter.value,
        search=search_term,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )