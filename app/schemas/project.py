from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, List

from app.schemas.place import PlaceResponse


class ProjectBase(BaseModel):
    """Base schema for a project"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    places: Optional[List[str]] = Field(
        default=None,
        description="List of external IDs of places from Art Institute API"
    )
    
    @field_validator('places')
    @classmethod
    def validate_places_count(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError("Maximum 10 places per project")
            if len(v) < 1:
                raise ValueError("Minimum 1 place per project")
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
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProjectWithPlacesResponse(ProjectResponse):
    """Response schema for a project with places"""
    places: List[PlaceResponse] = []
