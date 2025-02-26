from pydantic import BaseModel, Field
from enum import Enum
from typing import Any, Optional

class TaskStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in-progress'
    COMPLETED = 'completed'

class TaskPriority(int, Enum):
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5

class Task(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description='The title of the given task.'
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description='Describes the task, what is required.'
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description='The status of the task.'
    )
    priority: TaskPriority = Field(
        default=TaskPriority.VERY_LOW,
        description='Describes the priority of the task.'
    )
    
    class Config:
        json_schema_extra = {
            'example' : {
                'title': 'Pushups for the week',
                'description': '''Attempting to do 50 pushups a day for the next week.
                I would like to atleast have done a minimum of 30 per day.''',
                'status': 'pending',
                'priority': 1
            }
        }
        use_enum_values = True # API returns the Enum vals rather than name
        extra = 'forbid'
        title = 'Task'

# Defining a structure for what a typical response should look like
class MessageResponse(BaseModel):
    message: str = Field(
        ...,
        pattern='^(Success|Error)',
        description='This represents the status message'
    )
    data: Any = Field(
        default=None,
        description='Response data from the request'
    )
    status: int = Field(
        ...,
        ge=100,
        le=599,
        description='Status code of the response'
    )
    
    class Config:
        json_schema_extra = {
            'example' : {
                'message' : 'Error',
                'data' : None,
                'status' : 404
            }
        }