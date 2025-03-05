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