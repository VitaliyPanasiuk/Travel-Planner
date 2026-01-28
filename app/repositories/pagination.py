from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field, field_validator

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parameters for pagination"""
    page: int = Field(default=1, ge=1, description="Page number (starts from 1)")
    page_size: int = Field(default=10, ge=1, le=100, description="Number of items per page (max 100)")
    
    @field_validator('page', 'page_size')
    @classmethod
    def validate_positive(cls, v):
        if v < 1:
            raise ValueError("Must be positive")
        return v
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and page_size"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit (same as page_size)"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response with metadata"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @property
    def has_next(self) -> bool:
        """Check if there is a next page"""
        return self.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page"""
        return self.page > 1
