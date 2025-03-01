from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, Tuple

from app.db.models.task import Task as TaskModel
from app.schemas.task import Task as TaskSchema, TaskStatus, TaskPriority
from app.schemas.pagination import SortField, SortOrder

class TaskRepository:
    '''
    Repository for handling Task database operations.
    
    This class encapsulates all database interactions related to tasks,
    providing a clean, easy interface for the service layers.
    '''
    
    def __init__(self, db: Session):
        '''Initialise with a database session'''
        self.db = db
    
    def create(self, task: TaskSchema) -> TaskModel:
        '''
        Create a new task in the database.
        
        Args:
            task: The Pydantic schema containing task data
        
        Returns: 
            The created database model
        
        Raises:
            Exception: If there is a database error
        '''
        # converting Pydantic schema to SQLAlchemy model
        db_task = TaskModel(
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority
        )
        
        # Add to database session
        self.db.add(db_task)
        
        try:
            # Commit the transaction
            self.db.commit()
            # refresh model to get any database-generated vals (i.e. id)
            self.db.refresh(db_task)
            return db_task
        except Exception as e:
            # If an error is raised, roll the transaction back
            self.db.rollback()
            raise e
    
    def get_by_title(self, title: str) -> Optional[TaskModel]:
        '''
        Get a task by its title.
        
        Args:
            title: title to search for
        
        Returns:
            The task if found, None otherwise
        '''
        return self.db.query(TaskModel).filter(TaskModel.title == title).first()
    
    def get_all(self,
                status: Optional[str] = None,
                priority: Optional[int] = None,
                search: Optional[str] = None,
                sort_by: Optional[SortField] = None,
                sort_order: SortOrder = SortOrder.ASC,
                skip: int = 0,
                limit: Optional[int] = None) -> Tuple[list[TaskModel, int]]:
        '''
        Get tasks with filtering, sorting, and pagination.
        
        Args:
            status: Filter by task status
            priority: Filter by priority level
            search: Search for title and description
            sort_by: Field to sort by
            sort_order: Ascending or descending sort
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
        
        Returns:
            Tuple containing (list of tasks, total count)
        '''
        # begin building query
        query = self.db.query(TaskModel)
        
        # Aplly filters
        if status: 
            query = query.filter(TaskModel.status == status)
        if priority:
            query = query.filter(TaskModel.priority == priority)
        if search:
            # Search in both title and description
            query = query.filter(
                or_(
                    TaskModel.title.ilike(f'%{search}%'),
                    TaskModel.description.ilike(f'%{search}%')
                )
            )
        
        # Get total count before applying pagination
        # This is important for calculating pagination metadata
        total_count = query.count()
        
        # Apply sorting
        if sort_by:
            # get column to sort by
            sort_column = getattr(TaskModel, sort_by.value)
            
            # apply sort direction
            if sort_order == SortOrder.DESC:
                sort_column = sort_column.desc()
            
            query = query.order_by(sort_column)
        else:
            # Default sort by id if no sort field specified
            query = query.order_by(TaskModel.id)
        
        # Apply pagination
        if limit:
            query = query.offset(skip).limit(limit)
        else:
            query = query.offset(skip)
        
        # Execute query and return results with count
        return query.all(), total_count
    
    def update(self, title: str, task_update: TaskSchema) -> Optional[TaskModel]:
        '''
        Update an existing task.
        
        Args:
            title: The title of the task to update
            task_update: The new task data
        
        Returns:
            The updated task if found, None otherwise
        
        Raises:
            Exception: If there's a database error
        '''
        # Find the task by title
        db_task = self.get_by_title(title)
        
        if not db_task:
            return None

        # Update task attributes
        db_task.title = task_update.title
        db_task.description = task_update.description
        db_task.status = task_update.status
        db_task.priority = task_update.priority
        
        try:
            # Commit the changes
            self.db.commit()
            # Refresh to get the updated state
            self.db.refresh(db_task)
            return db_task
        except Exception as e:
            # Rollback on error
            self.db.rollback()
            raise e
    
    def delete(self, title: str) -> bool:
        '''
        Delete a task by title.
        
        Args: 
            title: The title of the task to delete
        
        Returns:
            True if the task was found and delete, False otherwise
        
        Raises:
            Exception: If there's a database error
        '''
        # Find the task by title
        db_task = self.get_by_title(title)
        
        if not db_task:
            return False
        
        try: 
            # Delete the task
            self.db.delete(db_task)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e