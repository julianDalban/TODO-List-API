from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title='To Do List API')

# Defining what the input values should look like.
class Task(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description='The title of the given task.',
        
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
        extra = 'forbid'
        title = 'Task'

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
        description='Response data from the request'
    ),
    status: int = Field(
        ...,
        ge=0,
        max_digits=3,
        description='Status code of the response'
    )
    
    class Config:
        schema_extra = {
            'example' : {
                'message' : 'Error',
                'data' : None,
                'status' : 404
            }
        }

class TitleInput(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description='The title of the given task.',
    )
    
    class Config:
        schema_extra = {
            'example' : {
                'title' : 'Pushups for the month'
            }
        }

# Defining the mechanism of storing the task
class TaskStore: 
    def __init__(self): # Initialize the tasks object to store all the tasks. Using a dict for accurate retrieval of specific task by title
        self.tasks: dict[Task] = dict() # Titles will be ensured to be unique
    
    def add_task(self, task: Task) -> bool: # Adding a task to the dict, returns bool based on if the operation was performed or not
        if task.title in self.tasks:
            return False
        self.tasks.update({task.title, task})
        return True
    
    def get_all_tasks(self) -> list[Task]: # Retrieves all tasks in the form of a list
        all_tasks = self.tasks.values()
        return all_tasks
    
    def update_task(self, title: str, updated_task: Task) -> bool: # Updates a task based on the given title
        if title not in self.tasks.keys():
            return False
        self.tasks[title] = updated_task
        return True
    
    def delete_task(self, title: str) -> True: # Deletes a task based on the given title
        if title not in self.tasks.keys():
            return False
        self.tasks.pop(title)
        return True
    
    def get_task_by_title(self, title: str) -> Task: # Retrieves a task specified by title
        if title not in self.tasks.keys():
            return None
        task = self.tasks.get(title)
        return task




