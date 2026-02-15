"""
Recipe Model
Stores recipes for meal planning
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Recipe(Base):
    """Recipe model for meal planning"""
    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    steps = Column(Text, nullable=False)  # HTML-formatted cooking instructions
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan", order_by="Ingredient.sort_order")

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "steps": self.steps,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "ingredient_count": len(self.ingredients) if self.ingredients else 0
        }


class Ingredient(Base):
    """Ingredient model for recipes"""
    __tablename__ = "ingredients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)  # "Chicken breast", "Carrot", etc.
    quantity_amount = Column(Numeric(10, 2), nullable=False)  # Numeric amount (e.g., 300, 1, 2)
    quantity_unit = Column(String(20), nullable=False)  # Unit (e.g., "g", "cup", "tsp")
    sort_order = Column(Integer, nullable=False, default=0)

    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "recipe_id": str(self.recipe_id),
            "name": self.name,
            "quantity_amount": str(self.quantity_amount),
            "quantity_unit": self.quantity_unit,
            "sort_order": self.sort_order
        }
