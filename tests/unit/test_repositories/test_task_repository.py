import pytest
from sqlalchemy.orm import Session

from app.db.repositories.task import TaskRepository
from app.schemas.task import Task as TaskSchema, TaskStatus, TaskPriority
from app.db.models.task import Task as TaskModel
from app.schemas.pagination import SortField, SortOrder

class TestTaskRepository:
    '''
    Test suite for the TaskRepository class.
    '''
    
    def test_create_task(self, db_session: Session):
        '''
        Test creating a new task
        '''
        # Setup 
        task_schema = TaskSchema(
            title='New Test Task',
            description='Testing task creation',
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        repository = TaskRepository(db_session)
        
        # Test
        result = repository.create(task_schema)
        
        # Verify 
        assert result is not None
        assert result.title == task_schema.title
        assert result.description == task_schema.description
        assert result.status == task_schema.status
        assert result.priority == task_schema.priority
        
        # make sure saved in db
        db_task = db_session.query(TaskModel).filter(TaskModel.title == 'New Test Task').first()
        assert db_task is not None
        
        # Clean Up
    
    def test_get_by_title(self, db_session: Session, sample_task: TaskModel):
        '''
        Test retrieving a task by title.
        '''
        # Setup
        repository = TaskRepository(db_session)
        
        # Test
        result = repository.get_by_title(sample_task.title)
        
        # Verify
        assert result is not None
        assert result.title == sample_task.title
        assert result.id == sample_task.id
    
    def test_get_by_title_not_found(self, db_session: Session):
        '''
        Test retrieving a non-existent task.
        '''
        # Setup
        repository = TaskRepository(db_session)
        
        # Test
        result = repository.get_by_title('Non-existent Task')
        
        # Verify
        assert result is None
    
    def test_update_task(self, db_session: Session, sample_task: TaskModel):
        # Setup
        repository = TaskRepository(db_session)
        updated_task = TaskSchema(
            title=sample_task.title,
            description='Updated description',
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH
        )
        
        # Test
        result = repository.update(sample_task.title, updated_task)
        
        # Verify
        assert result is not None
        assert result.title == updated_task.title
        assert result.description == 'Updated description'
        assert result.status == updated_task.status
        assert result.priority == updated_task.priority
    
    def test_delete_task(self, db_session: Session ,sample_task: TaskModel):
        '''Test deleting a task.'''
        # Setup
        repository = TaskRepository(db_session)
        
        # Test
        result = repository.delete(sample_task.title)
        
        # Verify
        assert result is True
        # make the db was actually changed
        db_task = db_session.query(TaskModel).filter(TaskModel.id == sample_task.id).first()
        assert db_task is None
    
    def test_get_all_no_filters(self, db_session: Session, sample_task: TaskModel):
        '''Test retrieving all task without filters.'''
        # Setup
        repository = TaskRepository(db_session)
        # adding second task
        second_task = TaskModel(
            title='Second Test Task',
            description='This is another test task',
            status='completed',
            priority=5
        )
        db_session.add(second_task)
        db_session.commit()
        
        # Test
        tasks, count = repository.get_all()
        
        # Verify
        assert count == 2
        assert len(tasks) == 2
        # check both tasks are in result
        task_titles = [task.title for task in tasks]
        assert sample_task.title in task_titles
        assert 'Second Test Task' in task_titles
    
    def test_get_all_with_status_filter(self, db_session: Session, sample_task: TaskModel):
        '''Test filtering tasks by status.'''
        # Setup
        repository = TaskRepository(db_session)
        completed_task = TaskModel(
            title='Completed Task',
            description='This is a completed task',
            status='completed',
            priority=1
        )
        db_session.add(completed_task)
        db_session.commit()
        
        # Test
        tasks, count = repository.get_all(status='completed')
        
        # Verify
        assert count == 1
        assert len(tasks) == 1
        assert tasks[0].title == 'Completed Task'
    
    def test_get_all_with_pagination(self, db_session: Session, sample_task: TaskModel):
        """Test pagination in get_all method."""
        # Setup - add multiple tasks to test pagination
        repository = TaskRepository(db_session)
        for i in range(1, 6):  # Add 5 more tasks
            db_session.add(TaskModel(
                title=f"Pagination Test Task {i}",
                description=f"Task for testing pagination {i}",
                status="pending",
                priority=i
            ))
        db_session.commit()
        
        # Test with different pagination parameters
        tasks_page1, total = repository.get_all(skip=0, limit=3)
        tasks_page2, _ = repository.get_all(skip=3, limit=3)
        
        # Verify
        assert total >= 6  # At least 6 tasks (5 new + sample_task)
        assert len(tasks_page1) == 3  # First page has exactly 3 items
        assert len(tasks_page2) > 0  # Second page has at least 1 item
        
        # Verify pagination works as expected - items don't overlap
        page1_titles = [task.title for task in tasks_page1]
        page2_titles = [task.title for task in tasks_page2]
        assert not any(title in page1_titles for title in page2_titles)
    
    def test_get_all_with_combined_filters(self, db_session: Session):
        """Test combining multiple filters in get_all method."""
        # Setup - add tasks with various combinations of status/priority
        repository = TaskRepository(db_session)
        tasks_data = [
            {"title": "Task A", "description": "High priority pending", "status": "pending", "priority": 4},
            {"title": "Task B", "description": "Medium priority in-progress", "status": "in-progress", "priority": 3},
            {"title": "Task C", "description": "High priority completed", "status": "completed", "priority": 4},
            {"title": "Task D", "description": "Low priority pending", "status": "pending", "priority": 2}
        ]
        
        for task_data in tasks_data:
            db_session.add(TaskModel(**task_data))
        db_session.commit()
        
        # Test with combined filters
        tasks, count = repository.get_all(
            status="pending",
            priority=4,
            sort_by=SortField.TITLE,
            sort_order=SortOrder.ASC
        )
        
        # Verify
        assert count == 1  # Only one task matches both filters
        assert tasks[0].title == "Task A"
        assert tasks[0].status == "pending"
        assert tasks[0].priority == 4
    
    def test_get_all_with_no_matching_results(self, db_session: Session):
        """Test get_all when no tasks match the filters."""
        repository = TaskRepository(db_session)
        
        # Use a filter that won't match any tasks
        tasks, count = repository.get_all(status="non-existent-status")
        
        # Verify
        assert count == 0
        assert len(tasks) == 0