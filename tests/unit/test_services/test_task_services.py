import pytest
from unittest.mock import MagicMock
from fastapi import status

from app.services.task_service import TaskService
from app.schemas.task import Task as TaskSchema, TaskStatus, TaskPriority
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
    
    # def 