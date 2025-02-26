from fastapi import HTTPException
from typing import Optional, Dict, Any

class CustomHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail = str,
        error_code: Optional[str] = None,
        headers : Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code