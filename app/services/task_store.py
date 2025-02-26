import re
from typing import Optional, List, Tuple

from app.schemas.task import Task, TaskPriority, TaskStatus
from app.schemas.pagination import SortField, SortOrder

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
    
    def get_task_by_title(self, title: str) -> Optional[Task]: # Retrieves a task specified by title
        return self.tasks.get(title)
    
    def get_filtered_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        search: Optional[str] = None,
        sort_by: Optional[SortField] = None,
        sort_order: SortOrder = SortOrder.ASC,
        skip: int=0,
        limit: Optional[int] = None
    ) -> tuple[list[Task], int]:
        
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
            reverse = sort_order == SortOrder.DESC
            filtered_tasks.sort(
                key=lambda x: getattr(x, sort_by),
                reverse=reverse
            )
            
        total_count = len(filtered_tasks)
        
        if limit:
            filtered_tasks = filtered_tasks[skip: skip + limit]
        else:
            filtered_tasks = filtered_tasks[skip:]
        
        return filtered_tasks, total_count