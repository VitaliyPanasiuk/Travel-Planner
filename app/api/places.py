from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.place_service import PlaceService
from app.services.project_service import ProjectService
from app.schemas.place import (
    PlaceCreate,
    PlaceUpdate,
    PlaceNotesUpdate,
    PlaceVisitedUpdate,
    PlaceResponse,
    PaginatedPlaceResponse,
    PlaceFilterParams
)

router = APIRouter(prefix="/projects/{project_id}/places", tags=["places"])


@router.post("", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
async def create_place(
    project_id: int,
    place_data: PlaceCreate,
    db: Session = Depends(get_db)
):
    """
    Add a place to an existing project.
    The backend validates that the place exists in the third-party API before storing it.
    """
    service = PlaceService(db)
    
    try:
        place = await service.create_place(project_id, place_data)
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
            detail="Failed to create place"
        )
    
    return PlaceResponse.model_validate(place)


@router.get("", response_model=PaginatedPlaceResponse)
def list_places(
    project_id: int,
    filters: PlaceFilterParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    List all places for a project with pagination and filtering.
    """
    project_service = ProjectService(db)
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    service = PlaceService(db)
    result = service.get_all_places(
        project_id=project_id,
        page=filters.page,
        page_size=filters.page_size,
        is_visited=filters.is_visited
    )
    
    return PaginatedPlaceResponse(
        items=[PlaceResponse.model_validate(place) for place in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
        has_next=result.has_next,
        has_previous=result.has_previous
    )


@router.get("/{place_id}", response_model=PlaceResponse)
def get_place(
    project_id: int,
    place_id: int,
    db: Session = Depends(get_db)
):
    """Get a single place within a project"""
    project_service = ProjectService(db)
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    service = PlaceService(db)
    place = service.get_place(project_id, place_id)
    
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found"
        )
    
    return PlaceResponse.model_validate(place)


@router.put("/{place_id}", response_model=PlaceResponse)
def update_place_notes(
    project_id: int,
    place_id: int,
    notes_data: PlaceNotesUpdate,
    db: Session = Depends(get_db)
):
    """
    Update notes for a place within a project.
    """
    project_service = ProjectService(db)
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    service = PlaceService(db)
    
    try:
        place = service.update_place_notes(project_id, place_id, notes_data)
        
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update place notes"
        )
    
    return PlaceResponse.model_validate(place)


@router.patch("/{place_id}/visited", response_model=PlaceResponse)
def mark_place_visited(
    project_id: int,
    place_id: int,
    visited_data: PlaceVisitedUpdate,
    db: Session = Depends(get_db)
):
    """
    Mark a place as visited or not visited within a project.
    Automatically updates project completion status.
    """
    project_service = ProjectService(db)
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    service = PlaceService(db)
    
    try:
        place = service.mark_place_visited(project_id, place_id, visited_data)
        
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        
        project_service.update_completion_status(project_id)
        
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update place visited status"
        )
    
    return PlaceResponse.model_validate(place)
