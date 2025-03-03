from sqlalchemy.orm import Session
from typing import Optional
from fastapi import status

from app.db.repositories.task import TaskRepository
from app.db.models.task import Task as TaskModel
from app.schemas.task import Task as TaskSchema
from app.core.exceptions import CustomHTTPException

class TaskService:
    '''
    Task service which will handle business logic and coordinates task operations.
    
    This service acts as an intermediary between the API endpoints and the db repo, handling conversions between models and schemas,
    and implementing business logic.
    '''
    
    def __init__(self, db: Session):
        '''Initialise with a db session.'''
        self.repository = TaskRepository(db)
    
    def create_task(self, task_schema: TaskSchema) -> TaskSchema:
        '''
        Create new task.
        
        Args: 
            task_schema: Pydantic schema containing task data
        
        Returns:
            Created task as Pydantic schema.
        
        Raises:
            CustomHTTPException: If task with same title already exists
        '''
        # check for existing task
        existing_task = self.repository.get_by_title(task_schema.title)
        if existing_task:
            raise CustomHTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Task with same title already exists',
                error_code='DUPLICATE_TASK'
            )
        
        # create task in db using repository
        db_task = self.repository.create(task_schema)
        
        # convert back to Pydantic schema and return
        return self._db_to_schema(db_task)

    def get_task_by_title(self, title: str) -> Optional[TaskSchema]:
        '''
        Get a task by its title.
        
        Args:
            title: title of the task to retrieve
        
        Returns:
            The task if found, None otherwise
        '''
        db_task = self.repository.get_by_title(title)
        if not db_task:
            return None
        
        return self._db_to_schema(db_task)
    
    def update_task(self, title: str, task_update: TaskSchema) -> TaskSchema:
        '''
        Update an existing task.
        
        Args:
            title: The title of the task to update
            task_update: The new task data
        
        Returns:
            Updated task as a Pydantic schema
        
        Raises:
            CustomHTTPException: If task not found or validation fails
        '''
        # check if titles match
        if title != task_update.title:
            raise CustomHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Cannot update a task name',
                error_code='TITLE_MISMATCH'
            )
        
        # update task in db
        db_task = self.repository.update(title, task_update)
        
        # raise exception if not found
        if not db_task:
            raise CustomHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task does not exist',
                error_code='TASK_NOT_FOUND'
            )
        
        # convert to Pydantic schema and return
        return self._db_to_schema(db_task)
    
    def _db_to_schema(self, db_task: TaskModel) -> TaskSchema:
        '''
        Convert a db model to a Pydantic schema. Private helper method.
        
        Args:
            db_task: The SQLAlchemy model to convert.
        
        Returns:
            Equivalent Pydantic schema
        '''
        return TaskSchema(
            title=db_task.title,
            description=db_task.description,
            status=db_task.status,
            priority=db_task.priority
        )