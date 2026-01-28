from __future__ import annotations

from sqlalchemy.orm import Session
from typing import Optional

from app.repositories.place_repository import PlaceRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.pagination import PaginatedResponse
from app.services.art_institute_api import ArtInstituteAPIService
from app.models.place import Place
from app.schemas.place import PlaceCreate, PlaceUpdate, PlaceNotesUpdate, PlaceVisitedUpdate


class PlaceService:
    """Service for place business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.place_repo = PlaceRepository(db)
        self.project_repo = ProjectRepository(db)
        self.api_service = ArtInstituteAPIService()
    
    async def create_place(
        self,
        project_id: int,
        place_data: PlaceCreate
    ) -> Place:
        """
        Add a place to an existing project.
        Validates that the place exists in Art Institute API.
        
        Args:
            project_id: ID of the project
            place_data: Place creation data
            
        Returns:
            Created place
            
        Raises:
            ValueError: If validation fails
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        
        if self.place_repo.exists_in_project(project_id, str(place_data.external_id)):
            raise ValueError(f"Place with external_id {place_data.external_id} already exists in this project")
        
        exists = await self.api_service.validate_place_exists(place_data.external_id)
        if not exists:
            raise ValueError(f"Place with ID {place_data.external_id} not found in Art Institute API")
        
        place = self.place_repo.create(
            project_id=project_id,
            external_id=place_data.external_id,
            notes=place_data.notes
        )
        
        return place
    
    def get_place(self, project_id: int, place_id: int) -> Optional[Place]:
        """Get place by ID within a project"""
        return self.place_repo.get_by_id(project_id, place_id)
    
    def get_all_places(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 10,
        is_visited: Optional[bool] = None
    ) -> PaginatedResponse[Place]:
        """Get all places for a project with pagination and filtering"""
        from app.repositories.pagination import PaginationParams
        
        pagination = PaginationParams(page=page, page_size=page_size)
        return self.place_repo.get_all_by_project(
            project_id=project_id,
            pagination=pagination,
            is_visited=is_visited
        )
    
    def update_place(
        self,
        project_id: int,
        place_id: int,
        place_data: PlaceUpdate
    ) -> Optional[Place]:
        """Update place"""
        update_data = place_data.model_dump(exclude_unset=True)
        return self.place_repo.update(
            project_id=project_id,
            place_id=place_id,
            **update_data
        )
    
    def update_place_notes(
        self,
        project_id: int,
        place_id: int,
        notes_data: PlaceNotesUpdate
    ) -> Optional[Place]:
        """Update place notes only"""
        return self.place_repo.update(
            project_id=project_id,
            place_id=place_id,
            notes=notes_data.notes
        )
    
    def mark_place_visited(
        self,
        project_id: int,
        place_id: int,
        visited_data: PlaceVisitedUpdate
    ) -> Optional[Place]:
        """Mark place as visited or not visited"""
        return self.place_repo.update(
            project_id=project_id,
            place_id=place_id,
            is_visited=visited_data.is_visited
        )