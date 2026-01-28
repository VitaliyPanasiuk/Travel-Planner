from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date
from math import ceil

from app.models.project import Project
from app.models.place import Place
from app.repositories.pagination import PaginationParams, PaginatedResponse


class ProjectRepository:
    """Repository for Project model operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        name: str,
        description: Optional[str] = None,
        start_date: Optional[date] = None
    ) -> Project:
        """Create a new project"""
        project = Project(
            name=name,
            description=description,
            start_date=start_date
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_all(
        self,
        pagination: Optional[PaginationParams] = None,
        is_completed: Optional[bool] = None,
        name_search: Optional[str] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None
    ) -> PaginatedResponse[Project]:
        """
        Get all projects with pagination and filtering
        
        Args:
            pagination: Pagination parameters (page, page_size)
            is_completed: Filter by completion status
            name_search: Search projects by name
            start_date_from: Filter projects with start_date >= this date
            start_date_to: Filter projects with start_date <= this date
        """
        query = self.db.query(Project)
        
        if is_completed is not None:
            query = query.filter(Project.is_completed == is_completed)
        
        if name_search:
            query = query.filter(Project.name == name_search)
        
        if start_date_from:
            query = query.filter(Project.start_date >= start_date_from)
        
        if start_date_to:
            query = query.filter(Project.start_date <= start_date_to)
        
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
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[date] = None
    ) -> Optional[Project]:
        """Update project"""
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        updates = {
            'name': name,
            'description': description,
            'start_date': start_date
        }
        
        for field, value in updates.items():
            if value is not None:
                setattr(project, field, value)
        
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def delete(self, project_id: int) -> bool:
        """
        Delete project.
        Returns False if project has visited places (cannot be deleted).
        """
        project = self.get_by_id(project_id)
        if not project:
            return False
        
        if project.has_visited_places():
            return False
        
        self.db.delete(project)
        self.db.commit()
        return True
    
    def update_completion_status(self, project: Project) -> Project:
        """Update project completion status based on places"""
        project.is_completed = project.check_completion()
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_places_count(self, project_id: int) -> int:
        """Get count of places in project"""
        return self.db.query(Place).filter(Place.project_id == project_id).count()
    
    def has_place_with_external_id(self, project_id: int, external_id: str) -> bool:
        """Check if project already has a place with given external_id"""
        place = self.db.query(Place).filter(
            and_(
                Place.project_id == project_id,
                Place.external_id == external_id
            )
        ).first()
        return place is not None
