from fastapi import APIRouter, Path, Query, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.task import Task, TaskStatus, TaskPriority, MessageResponse
from app.schemas.pagination import SortField, SortOrder, PaginatedResponse
from app.services.task_service import TaskService
from app.core.exceptions import CustomHTTPException
from app.db.session import get_db


router = APIRouter()

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
    ),
    db: Session = Depends(get_db) # db dependency
) -> MessageResponse:
    try:
        # create service with injected db session
        service = TaskService(db)
        
        # use service
        filtered_tasks, total_count = service.get_filtered_tasks(
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
            data=pagination.model_dump(),
            status=200
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

@router.get('/{title}')
async def read_task(
    title: str = Path(
        ...,
        min_length=1,
        max_length=50,
        description='Title of the task to retrieve'
    ),
    db: Session = Depends(get_db)
) -> MessageResponse:
    try:
        service = TaskService(db) # create service with injected db session
        task = service.get_task_by_title(title) # use service
        
        if not task:
            raise CustomHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task could not be found',
                error_code='TASK_NOT_FOUND'
            )
        return MessageResponse(
            message='Success',
            data=task.model_dump(),
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
    input_data: Task,
    db: Session = Depends(get_db) # Inject db session
) -> MessageResponse:
    try:
        # create service with injected db session
        service = TaskService(db)
        
        # create task using service
        task = service.create_task(input_data)
        
        return MessageResponse(
            message='Success',
            data=task.model_dump(),
            status=201,
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
    ),
    db: Session = Depends(get_db)
) -> MessageResponse:
    try:
        service = TaskService(db) # create service with injected db session
        service.update_task(title, input_data) # update task using service (validation and error handled)
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
    ),
    db : Session = Depends(get_db)
) -> MessageResponse:
    try:
        service = TaskService(db)
        service.delete_task(title)
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