from pydantic import BaseModel, Field, field_validator, field_serializer
from datetime import date, datetime
from typing import Optional, List

from app.schemas.place import PlaceResponse
from app.repositories.pagination import PaginationParams


class ProjectBase(BaseModel):
    """Base schema for a project"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    places: Optional[List[int]] = Field(
        default=None,
        description="List of external IDs of places from Art Institute API"
    )
    
    @field_validator('places', mode='before')
    @classmethod
    def validate_places(cls, v):
        """Handle None, empty list, and validate places"""
        if v is None:
            return None
        if isinstance(v, list):
            if len(v) == 0:
                return None
            if len(v) > 10:
                raise ValueError("Maximum 10 places per project")
        return v


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None


class ProjectResponse(ProjectBase):
    """Response schema for a project"""
    id: int
    is_completed: bool
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


class ProjectWithPlacesResponse(ProjectResponse):
    """Response schema for a project with places"""
    places: List[PlaceResponse] = []


class PaginatedProjectResponse(BaseModel):
    """Paginated response schema for projects"""
    items: List[ProjectResponse]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class PaginatedProjectWithPlacesResponse(BaseModel):
    """Paginated response schema for projects with places"""
    items: List[ProjectWithPlacesResponse]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class ProjectFilterParams(BaseModel):
    """Schema for project filtering and pagination parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    is_completed: Optional[bool] = None
    name_search: Optional[str] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    
    def to_pagination(self) -> PaginationParams:
        """Convert to PaginationParams"""
        return PaginationParams(page=self.page, page_size=self.page_size)
