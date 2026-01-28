from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Place(Base):
    """Place model for travel planning"""
    
    __tablename__ = "places"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id = Column(String, nullable=False, index=True)
    notes = Column(String, nullable=True)
    is_visited = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="places")
    
    __table_args__ = (
        UniqueConstraint('project_id', 'external_id', name='uq_project_external_id'),
    )
