from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from typing import Optional, List

from app.repositories.pagination import PaginationParams


class PlaceBase(BaseModel):
    """Base schema for place"""
    external_id: int = Field(..., description="ID места из Art Institute API")
    notes: Optional[str] = Field(None, max_length=2000)


class PlaceCreate(PlaceBase):
    """Schema for creating a place"""
    pass


class PlaceUpdate(BaseModel):
    """Schema for updating a place"""
    notes: Optional[str] = Field(None, max_length=2000)
    is_visited: Optional[bool] = None


class PlaceNotesUpdate(BaseModel):
    """Schema for updating place notes"""
    notes: Optional[str] = Field(None, max_length=2000)


class PlaceVisitedUpdate(BaseModel):
    """Schema for updating place visited status"""
    is_visited: bool = Field(..., description="Whether the place is visited")


class PlaceResponse(PlaceBase):
    """Response schema for a place"""
    id: int
    project_id: int
    is_visited: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime) -> str:
        """Convert datetime to ISO format string"""
        return value.isoformat() if value else None
    
    @field_serializer('updated_at')
    def serialize_updated_at(self, value: Optional[datetime]) -> Optional[str]:
        """Convert datetime to ISO format string"""
        return value.isoformat() if value else None
    
    class Config:
        from_attributes = True


class PaginatedPlaceResponse(BaseModel):
    """Paginated response schema for places"""
    items: List[PlaceResponse]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class PlaceFilterParams(BaseModel):
    """Schema for place filtering and pagination parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    is_visited: Optional[bool] = None
    
    def to_pagination(self) -> PaginationParams:
        """Convert to PaginationParams"""
        return PaginationParams(page=self.page, page_size=self.page_size)
