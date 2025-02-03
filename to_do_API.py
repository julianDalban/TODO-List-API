from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional
from enum import Enum
import re

# Convention naming for this file would be main.py

app = FastAPI(title='To Do List API')

class SortOrder(str, Enum):
    asc = 'asc'
    desc = 'desc'

# Defining what the input values should look like.
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
    status: str = Field(
        ...,
        pattern="^(pending|in-progress|completed)$",
        description='The status of the task.'
    )
    priority: int = Field(
        ...,
        ge=1,
        le=5,
        description='Describes the priority of the task.'
    )
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = {'pending', 'in-progress', 'completed'}
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v
    
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
        extra = 'forbid'
        title = 'Task'

# Defining a structure for what a typical response should look like
class MessageResponse(BaseModel):
    message: str = Field(
        ...,
        pattern='^(Success|Error)',
        description='This represents the status message',
        examples= ['Success', 'Error']
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


# Defining the mechanism of storing the task
class TaskStore: 
    def __init__(self): # Initialize the tasks object to store all the tasks. Using a dict for accurate retrieval of specific task by title
        self.tasks: dict[str, Task] = {} # Titles will be ensured to be unique
    
    def add_task(self, task: Task) -> bool: # Adding a task to the dict, returns bool based on if the operation was performed or not
        if task.title in self.tasks:
            return False
        self.tasks[task.title] = task
        return True
    
    def get_all_tasks(self) -> list[Task]: # Retrieves all tasks in the form of a list
        all_tasks = list(self.tasks.values())
        return all_tasks
    
    def update_task(self, title: str, updated_task: Task) -> bool: # Updates a task based on the given title
        if title not in self.tasks.keys():
            return False
        self.tasks[title] = updated_task
        return True
    
    def delete_task(self, title: str) -> bool: # Deletes a task based on the given title
        if title not in self.tasks.keys():
            return False
        self.tasks.pop(title)
        return True
    
    def get_task_by_title(self, title: str) -> Task: # Retrieves a task specified by title
        if title not in self.tasks.keys():
            return None
        task = self.tasks.get(title)
        return task
    
    def get_filtered_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: SortOrder = SortOrder.asc
    ) -> list[Task]:
        
        filtered_tasks = list(self.tasks.values())
        
        if status:
            filtered_tasks = [
                task for task in filtered_tasks if task.status == status
            ]
        
        if priority:
            filtered_tasks = [
                task for task in filtered_tasks if task.priority == priority
            ]
        
        if search:
            search_pattern = re.compile(search, re.IGNORECASE)
            filtered_tasks = [
                task for task in filtered_tasks
                if search_pattern.search(task.title) or search_pattern.search(task.description)
            ]

        if sort_by:
            reverse = sort_order == SortOrder.desc
            filtered_tasks.sort(
                key=lambda x : getattr(x, sort_by),
                reverse=reverse
            )
            
        return filtered_tasks

task_store = TaskStore()

@app.get('/tasks')
async def read_all_tasks(
    status: Optional[str] = Query(
        None,
        description='Filter tasks by status (pending, in-progress, completed)'
    ),
    priority: Optional[int] = Query(
        None,
        ge=1,
        le=5,
        description='Filter tasks by priority level (1-5)'
    ),
    search: Optional[str] = Query(
        None,
        min_length=1,
        description='Search in task titles and descriptions'
    ),
    sort_by: Optional[str] = Query(
        None,
        pattern='^(title|priority|status)$',
        description='Field to sort by'
    ),
    sort_order: SortOrder = Query(
        SortOrder.asc,
        description='Sort order (asc or desc)'
    )
) -> MessageResponse:
    try:
        return MessageResponse(
            message='Success',
            data= task_store.get_all_tasks(),
            status=200
        ).model_dump()
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

@app.get('/tasks/{title}')
async def read_task(
    title: str = Path(
        ...,
        min_length=1,
        max_length=50,
        description='Title of the task to retrieve'
    )
) -> MessageResponse:
    try:
        task = task_store.get_task_by_title(title)
        if not task:
            return MessageResponse(
                message='Error',
                data='Task could not be found',
                status=404
            ).model_dump()
        else:
            return MessageResponse(
                message='Success',
                data=task,
                status=200
            ).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

@app.post('/tasks')
async def create_task(
    input_data: Task
) -> MessageResponse:
    try:
        if not task_store.add_task(input_data):
            return MessageResponse(
                message='Error',
                data='Task with the same title already exists',
                status=409
            ).model_dump()
        else:
            return MessageResponse(
                message='Success',
                data='Task successfully added',
                status=200
            ).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put('/tasks/{title}')
async def update_given_task(
    input_data: Task,
    title: str = Path(
        ...,
        min_length=1,
        max_length=50,
        description='Title of the task to retrieve'
    )
) -> MessageResponse:
    try:
        if title != input_data.title:
            return MessageResponse(
                message='Error',
                data='Cannot update a task name',
                status=404
            ).model_dump()
        elif not task_store.update_task(title, input_data):
            return MessageResponse(
                message='Error',
                data='Task does not exist',
                status=404
            ).model_dump()
        else:
            return MessageResponse(
                message='Success',
                data='Task successfully updated',
                status=200
            ).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete('/tasks/{title}')
async def delete_given_task(
    title: str = Path(
        ...,
        min_length=1,
        max_length=50,
        description='Title of the task to retrieve'
    )
) -> MessageResponse:
    try:
        if not task_store.delete_task(title):
            return MessageResponse(
                message='Error',
                data='Task not found',
                status=404
            ).model_dump()
        else:
            return MessageResponse(
                message='Success',
                data='Task successfully deleted',
                status=200
            ).model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))