from enum import Enum
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

class SortField(str, Enum):
    TITLE = 'title'
    PRIORITY = 'priority'
    STATUS = 'status'

class SortOrder(str, Enum):
    ASC = 'asc'
    DESC = 'desc'

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: Optional[int]
    
    @property
    def has_more(self) -> bool:
        '''Return True if there are more items after this page'''
        if self.limit is None:
            return False
        return self.skip + len(self.items) < self.total
    
    class Config:
        json_schema_extra = {
            'example': {
                'items': [],
                'total': 100,
                'skip': 0,
                'limit': 10
            }
        }