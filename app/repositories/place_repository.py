from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from math import ceil

from app.models.place import Place
from app.models.project import Project
from app.repositories.pagination import PaginationParams, PaginatedResponse


class PlaceRepository:
    """Repository for Place model operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        project_id: int,
        external_id: str,
        notes: Optional[str] = None
    ) -> Place:
        """Create a new place in project"""
        place = Place(
            project_id=project_id,
            external_id=external_id,
            notes=notes
        )
        self.db.add(place)
        self.db.commit()
        self.db.refresh(place)
        return place
    
    def get_by_id(self, project_id: int, place_id: int) -> Optional[Place]:
        """Get place by ID within a project"""
        return self.db.query(Place).filter(
            and_(
                Place.id == place_id,
                Place.project_id == project_id
            )
        ).first()
    
    def get_all_by_project(
        self,
        project_id: int,
        pagination: Optional[PaginationParams] = None,
        is_visited: Optional[bool] = None,
        external_id_search: Optional[str] = None
    ) -> PaginatedResponse[Place]:
        """
        Get all places for a project with pagination and filtering
        
        Args:
            project_id: ID of the project
            pagination: Pagination parameters (page, page_size)
            is_visited: Filter by visited status
            external_id_search: Search places by external_id
        """
        query = self.db.query(Place).filter(Place.project_id == project_id)
        
        if is_visited is not None:
            query = query.filter(Place.is_visited == is_visited)
        
        if external_id_search:
            query = query.filter(Place.external_id == external_id_search)
        
        total = query.count()
        
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
            page = pagination.page
            page_size = pagination.page_size
        else:
            page = 1
            page_size = total if total > 0 else 1
        
        items = query.all()
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    def update(
        self,
        project_id: int,
        place_id: int,
        notes: Optional[str] = None,
        is_visited: Optional[bool] = None
    ) -> Optional[Place]:
        """Update place"""
        place = self.get_by_id(project_id, place_id)
        if not place:
            return None
        
        updates = {
            'notes': notes,
            'is_visited': is_visited
        }
        
        for field, value in updates.items():
            if value is not None:
                setattr(place, field, value)
        
        self.db.commit()
        self.db.refresh(place)
        return place
    
    def mark_as_visited(self, project_id: int, place_id: int) -> Optional[Place]:
        """Mark place as visited"""
        return self.update(project_id, place_id, is_visited=True)
    
    def exists_in_project(self, project_id: int, external_id: str) -> bool:
        """Check if place with external_id already exists in project"""
        place = self.db.query(Place).filter(
            and_(
                Place.project_id == project_id,
                Place.external_id == external_id
            )
        ).first()
        return place is not None
    
    def count_by_project(self, project_id: int) -> int:
        """Count places in project"""
        return self.db.query(Place).filter(Place.project_id == project_id).count()
