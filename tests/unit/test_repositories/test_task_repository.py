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