from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.project_service import ProjectService
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithPlacesResponse,
    ProjectFilterParams,
    PaginatedProjectResponse,
    PaginatedProjectWithPlacesResponse
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectWithPlacesResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new travel project.
    Can include places from Art Institute API in the same request.
    """
    service = ProjectService(db)
    
    try:
        project = await service.create_project(project_data)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )
    
    return ProjectWithPlacesResponse.model_validate(project)


@router.get("", response_model=PaginatedProjectWithPlacesResponse)
def list_projects(
    filters: ProjectFilterParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    List all travel projects with pagination and filtering.
    Returns projects with their places.
    """
    service = ProjectService(db)
    result = service.get_all_projects(filters)
    
    return PaginatedProjectWithPlacesResponse(
        items=[ProjectWithPlacesResponse.model_validate(project) for project in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        has_next=result.has_next,
        has_previous=result.has_previous
    )


@router.get("/{project_id}", response_model=ProjectWithPlacesResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get a single travel project by ID"""
    service = ProjectService(db)
    project = service.get_project(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return ProjectWithPlacesResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update travel project information"""
    service = ProjectService(db)
    
    try:
        project = service.update_project(project_id, project_data)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )
    
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a travel project.
    Cannot delete if any places are marked as visited.
    """
    service = ProjectService(db)
    
    try:
        project = service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        deleted = service.delete_project(project_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete project with visited places"
            )
        
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )
    
    return None
