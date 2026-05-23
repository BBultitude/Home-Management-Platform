"""
Week Plan Model
Stores weekly meal planning assignments
"""

from datetime import date, datetime, timedelta
from sqlalchemy import Column, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base

_RECIPE_FK = "recipes.id"
_ON_DELETE = "SET NULL"


class WeekPlan(Base):
    """Weekly meal plan model"""
    __tablename__ = "week_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    week_starting = Column(Date, nullable=False, unique=True)  # Monday of the week
    monday_meal_id = Column(UUID(as_uuid=True), ForeignKey(_RECIPE_FK, ondelete=_ON_DELETE), nullable=True)
    tuesday_meal_id = Column(UUID(as_uuid=True), ForeignKey(_RECIPE_FK, ondelete=_ON_DELETE), nullable=True)
    wednesday_meal_id = Column(UUID(as_uuid=True), ForeignKey(_RECIPE_FK, ondelete=_ON_DELETE), nullable=True)
    thursday_meal_id = Column(UUID(as_uuid=True), ForeignKey(_RECIPE_FK, ondelete=_ON_DELETE), nullable=True)
    friday_meal_id = Column(UUID(as_uuid=True), ForeignKey(_RECIPE_FK, ondelete=_ON_DELETE), nullable=True)
    saturday_meal_id = Column(UUID(as_uuid=True), ForeignKey(_RECIPE_FK, ondelete=_ON_DELETE), nullable=True)
    sunday_meal_id = Column(UUID(as_uuid=True), ForeignKey(_RECIPE_FK, ondelete=_ON_DELETE), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships (optional - for eager loading)
    monday_meal = relationship("Recipe", foreign_keys=[monday_meal_id])
    tuesday_meal = relationship("Recipe", foreign_keys=[tuesday_meal_id])
    wednesday_meal = relationship("Recipe", foreign_keys=[wednesday_meal_id])
    thursday_meal = relationship("Recipe", foreign_keys=[thursday_meal_id])
    friday_meal = relationship("Recipe", foreign_keys=[friday_meal_id])
    saturday_meal = relationship("Recipe", foreign_keys=[saturday_meal_id])
    sunday_meal = relationship("Recipe", foreign_keys=[sunday_meal_id])

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "week_starting": self.week_starting.isoformat(),
            "monday_meal_id": str(self.monday_meal_id) if self.monday_meal_id else None,
            "tuesday_meal_id": str(self.tuesday_meal_id) if self.tuesday_meal_id else None,
            "wednesday_meal_id": str(self.wednesday_meal_id) if self.wednesday_meal_id else None,
            "thursday_meal_id": str(self.thursday_meal_id) if self.thursday_meal_id else None,
            "friday_meal_id": str(self.friday_meal_id) if self.friday_meal_id else None,
            "saturday_meal_id": str(self.saturday_meal_id) if self.saturday_meal_id else None,
            "sunday_meal_id": str(self.sunday_meal_id) if self.sunday_meal_id else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @staticmethod
    def get_monday_of_week(target_date: date) -> date:
        """Get the Monday of the week for a given date"""
        # Python weekday(): Monday=0, Sunday=6
        days_since_monday = target_date.weekday()
        monday = target_date - timedelta(days=days_since_monday)
        return monday
