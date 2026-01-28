from pydantic import BaseModel, Field
from typing import Optional


class PlaceBase(BaseModel):
    """Base schema for place"""
    external_id: str = Field(..., description="ID места из Art Institute API")
    notes: Optional[str] = Field(None, max_length=2000)


class PlaceCreate(PlaceBase):
    """Schema for creating a place"""
    pass


class PlaceUpdate(BaseModel):
    """Schema for updating a place"""
    notes: Optional[str] = Field(None, max_length=2000)
    is_visited: Optional[bool] = None


class PlaceResponse(PlaceBase):
    """Response schema for a place"""
    id: int
    project_id: int
    is_visited: bool
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True
