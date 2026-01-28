from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Project(Base):
    """Project model for travel planning"""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    places = relationship("Place", back_populates="project", cascade="all, delete-orphan")
    
    def check_completion(self) -> bool:
        """Checks if the project is completed. The project is completed if all places are marked as visited."""
        if not self.places:
            return False
        return all(place.is_visited for place in self.places)
    
    def has_visited_places(self) -> bool:
        """Checks if the project has visited places"""
        return any(place.is_visited for place in self.places)
