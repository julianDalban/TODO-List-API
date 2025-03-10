from sqlalchemy.orm import Session
from typing import Optional, Tuple
from fastapi import status

from app.db.repositories.task import TaskRepository
from app.db.models.task import Task as TaskModel
from app.schemas.task import Task as TaskSchema, TaskStatus, TaskPriority
from app.core.exceptions import CustomHTTPException
from app.schemas.pagination import SortField, SortOrder

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

    def delete_task(self, title: str) -> bool:
        '''
        Delete a task by title.
        
        Args:
            title: The title of the task to delete
        
        Returns:
            True if task was deleted, raises exception otherwise
        
        Raises:
            CustomHTTPException: If task not found
        '''
        # del task from db
        deleted = self.repository.delete(title)
        
        # if task not found
        if not deleted:
            raise CustomHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task not found',
                error_code='TASK_NOT_FOUND'
            )
        
        return True
    
    def get_filtered_tasks(
        self,
        status: Optional[TaskStatus ] = None,
        priority: Optional[TaskPriority] = None,
        search: Optional[str] = None,
        sort_by: Optional[SortField] = None,
        sort_order: SortOrder = SortOrder.ASC,
        skip: int = 0,
        limit: Optional[int] = None
    ) -> Tuple[list[TaskSchema], int]:
        '''
        Get tasks with filtering, sorting, and paginations.
        
        Args:
            status: Filter by task status
            priority: Filter by priority level
            search: Search for title and description
            sort_by: Field to sort by
            sort_order: Ascending or descending sort
            skip: Number of records to skip (pagination)
            limit: Max num of records to return
        
        Returns:
            Tuple containing (list of tasks as Pydantic schemas, total count)
        '''
        # get filtered tasks from repo
        db_tasks, total_count = self.repository.get_all(
            status=status.value if status else None,
            priority=priority.value if priority else None,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        # convert db models to Pydantic schemas
        task_schemas = [self._db_to_schema(task) for task in db_tasks]
        
        return task_schemas, total_count
    
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