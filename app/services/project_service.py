from __future__ import annotations

from sqlalchemy.orm import Session
from typing import Optional

from app.repositories.project_repository import ProjectRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.pagination import PaginatedResponse
from app.services.art_institute_api import ArtInstituteAPIService
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectFilterParams


class ProjectService:
    """Service for project business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.place_repo = PlaceRepository(db)
        self.api_service = ArtInstituteAPIService()
    
    async def create_project(
        self,
        project_data: ProjectCreate
    ) -> Project:
        """
        Create a new project with optional places.
        
        Args:
            project_data: Project creation data
            
        Returns:
            Created project
            
        Raises:
            ValueError: If validation fails
        """
        if project_data.places:
            if len(project_data.places) != len(set(project_data.places)):
                raise ValueError("Duplicate places in request")
            
            for external_id in project_data.places:
                exists = await self.api_service.validate_place_exists(external_id)
                if not exists:
                    raise ValueError(f"Place with ID {external_id} not found in Art Institute API")
        
        project = self.project_repo.create(
            name=project_data.name,
            description=project_data.description,
            start_date=project_data.start_date
        )
        
        if project_data.places:
            for external_id in project_data.places:
                self.place_repo.create(
                    project_id=project.id,
                    external_id=external_id
                )
        
        self.db.refresh(project)
        project = self.project_repo.get_by_id(project.id, load_places=True)
        return project
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        return self.project_repo.get_by_id(project_id)
    
    def get_all_projects(
        self,
        filters: ProjectFilterParams
    ) -> PaginatedResponse[Project]:
        """Get all projects with pagination and filtering"""
        return self.project_repo.get_all(
            pagination=filters.to_pagination(),
            is_completed=filters.is_completed,
            name_search=filters.name_search,
            start_date_from=filters.start_date_from,
            start_date_to=filters.start_date_to
        )
    
    def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate
    ) -> Optional[Project]:
        """Update project"""
        update_data = project_data.model_dump(exclude_unset=True)
        return self.project_repo.update(
            project_id=project_id,
            **update_data
        )
    
    def delete_project(self, project_id: int) -> bool:
        """
        Delete project.
        Returns False if project has visited places.
        """
        return self.project_repo.delete(project_id)
    
    def update_completion_status(self, project_id: int) -> Optional[Project]:
        """Update project completion status based on places"""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return None
        return self.project_repo.update_completion_status(project)
