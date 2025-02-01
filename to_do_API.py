from fastapi import FastAPI, HTTPException
from pydantic  import BaseModel, Field

app = FastAPI(title='To Do List API')

# Defining what the input values should look like.
class Task(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description='The title of the given task.'
    ),
    description: str = Field(
        default=None,
        min_length=1,
        max_length=1000,
        description='Describes the task, what is required.'
    ),
    status: str = Field(
        ...,
        pattern="^(pending|in-progress|completed)$",
        description='The status of the task.'
    ),
    priority: int = Field(
        ...,
        ge=1,
        le=5,
        description='Describes the priority of the task.'
    )
    class Config:
        schema_extra = {
            'example' : {
                'title': 'Pushups for the week',
                'description': '''Attempting to do 50 pushups a day for the next week.
                I would like to atleast have done a minimum of 30 per day.''',
                'status': 'pending',
                'priority': 1
            }
        }

# Defining a structure for what a typical response should look like
class MessageResponse(BaseModel):
    message: str = Field(
        ...,
        pattern='^(Success|Error)',
        description='This represents the status message',
        examples= ['Success', 'Error']
    ),
    data: str = Field(
        default=None,
        description='Response data from the '
    )


# Defining the mechanism of storing the task
class TaskStore: 
    def __init__(self):
        self.tasks = dict[Task] = dict()
    
    def add_task(self, Task):
        if Task.title in self.tasks: