from fastapi import APIRouter, Path, Query, status, HTTPException
from typing import Optional

from app.schemas.task import Task, TaskStatus, TaskPriority, MessageResponse
from app.schemas.pagination import SortField, SortOrder, PaginatedResponse
from app.services.task_store import TaskStore
from app.core.exceptions import CustomHTTPException

router = APIRouter()
task_store = TaskStore()

@router.get('')
async def read_tasks(
    status: Optional[TaskStatus] = Query(
        None,
        description='Filter tasks by status (pending, in-progress, completed)'
    ),
    priority: Optional[TaskPriority] = Query(
        None,
        description='Filter tasks by priority level (1-5)'
    ),
    search: Optional[str] = Query(
        None,
        min_length=1,
        description='Search in task titles and descriptions'
    ),
    sort_by: Optional[SortField] = Query(
        None,
        description='Field to sort by'
    ),
    sort_order: SortOrder = Query(
        SortOrder.ASC,
        description='Sort order (asc or desc)'
    ),
    skip: int = Query(
        0, 
        ge=0,
        description='Number of items to skip (for pagination)'
    ),
    limit: Optional[int] = Query(
        10,
        ge=1,
        le=100,
        description='Maximum number of items to return (for pagination)'
    )
) -> MessageResponse:
    try:
        filtered_tasks, total_count = task_store.get_filtered_tasks(
            status=status,
            priority=priority,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        pagination = PaginatedResponse[Task](
            items=filtered_tasks,
            total=total_count,
            skip=skip,
            limit=limit
        )
        return MessageResponse(
            message='Success',
            data= pagination.model_dump(),
            status=200
        ).model_dump()
    except ValueError as e:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            error_code='VALIDATION_ERROR'
        )
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
            error_code='INTERNAL_ERROR'
        )

@router.get('/{title}')
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
            raise CustomHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task could not be found',
                error_code='TASK_NOT_FOUND'
            )
        return MessageResponse(
            message='Success',
            data=task,
            status=200
        ).model_dump()
    except CustomHTTPException:
        raise 
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
            error_code='INTERNAL_ERROR'
        )

@router.post('', status_code=status.HTTP_201_CREATED)
async def create_task(
    input_data: Task
) -> MessageResponse:
    try:
        if not task_store.add_task(input_data):
            raise CustomHTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Task with same title already exists',
                error_code='DUPLICATE_TASK'
            )
        return MessageResponse(
            message='Success',
            data='Task successfully created',
            status=201
        ).model_dump()
    except CustomHTTPException:
        raise
    except ValueError as e:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            error_code='VALIDATION_ERROR'
        )
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
            error_code='INTERNAL_ERROR'
        )

@router.put('/{title}')
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
            raise CustomHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Cannot update a task name',
                error_code='TITLE_MISMATCH'
            )
        elif not task_store.update_task(title, input_data):
            raise CustomHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task does not exist',
                error_code='TASK_NOT_FOUND'
            )
        return MessageResponse(
            message='Success',
            data='Task successfully updated',
            status=200
        ).model_dump()
    except CustomHTTPException:
        raise
    except ValueError as e:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            error_code="VALIDATION_ERROR"
        )
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
            error_code='INTERNAL_ERROR'
        )

@router.delete('/{title}')
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
            raise CustomHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task not found',
                error_code='TASK_NOT_FOUND'
            )
        return MessageResponse(
            message='Success',
            data='Task successfully deleted',
            status=200
        ).model_dump()
    except CustomHTTPException:
        raise
    except ValueError as e:
        raise CustomHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            error_code="VALIDATION_ERROR"
        )
    except Exception as e:
        raise CustomHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
            error_code='INTERNAL_ERROR'
        )