"""
Priority Item Service
Handles CRUD operations and scoring for repair/upgrade prioritization
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.priority_item import PriorityItem, PriorityStatus
from app.models.project import Project, ProjectStatus


class PriorityItemService:
    """Service for priority item operations"""

    @staticmethod
    def create_priority_item(
        db: Session,
        description: str,
        cost: Decimal,
        severity: int,
        frequency: int
    ) -> PriorityItem:
        """Create a new priority item with auto-calculated scores"""
        if cost <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cost must be greater than 0"
            )

        if not (1 <= severity <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Severity must be between 1 and 5"
            )

        if not (1 <= frequency <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Frequency must be between 1 and 5"
            )

        # Calculate scores
        scores = PriorityItem.calculate_scores(cost, severity, frequency)

        priority_item = PriorityItem(
            description=description,
            cost=cost,
            severity=severity,
            frequency=frequency,
            benefit_score=scores["benefit_score"],
            cost_score=scores["cost_score"],
            net_score=scores["net_score"],
            status=PriorityStatus.PENDING.value
        )

        db.add(priority_item)
        db.commit()
        db.refresh(priority_item)

        return priority_item

    @staticmethod
    def get_priority_item(db: Session, item_id: UUID) -> PriorityItem:
        """Get a priority item by ID"""
        item = db.query(PriorityItem).filter(PriorityItem.id == item_id).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Priority item not found"
            )

        return item

    @staticmethod
    def list_priority_items(
        db: Session,
        status_filter: Optional[PriorityStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[PriorityItem]:
        """
        List priority items sorted by net_score (highest priority first)

        Args:
            db: Database session
            status_filter: Optional status filter
            limit: Maximum entries to return
            offset: Pagination offset

        Returns:
            List of PriorityItem objects sorted by net_score DESC
        """
        query = db.query(PriorityItem)

        if status_filter:
            query = query.filter(PriorityItem.status == status_filter.value)

        # Sort by net_score descending (highest priority first)
        query = query.order_by(PriorityItem.net_score.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_priority_item(
        db: Session,
        item_id: UUID,
        description: Optional[str] = None,
        cost: Optional[Decimal] = None,
        severity: Optional[int] = None,
        frequency: Optional[int] = None,
        status_update: Optional[PriorityStatus] = None
    ) -> PriorityItem:
        """Update a priority item and recalculate scores if needed"""
        item = PriorityItemService.get_priority_item(db, item_id)

        # Track if recalculation is needed
        recalculate = False

        if description is not None:
            item.description = description

        if cost is not None:
            if cost <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cost must be greater than 0"
                )
            item.cost = cost
            recalculate = True

        if severity is not None:
            if not (1 <= severity <= 5):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Severity must be between 1 and 5"
                )
            item.severity = severity
            recalculate = True

        if frequency is not None:
            if not (1 <= frequency <= 5):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Frequency must be between 1 and 5"
                )
            item.frequency = frequency
            recalculate = True

        # Recalculate scores if any scoring parameter changed
        if recalculate:
            scores = PriorityItem.calculate_scores(item.cost, item.severity, item.frequency)
            item.benefit_score = scores["benefit_score"]
            item.cost_score = scores["cost_score"]
            item.net_score = scores["net_score"]

        if status_update is not None:
            item.status = status_update.value
            if status_update in [PriorityStatus.DONE, PriorityStatus.DISMISSED]:
                item.completed_at = datetime.utcnow()

        item.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    def delete_priority_item(db: Session, item_id: UUID) -> None:
        """Delete a priority item"""
        item = PriorityItemService.get_priority_item(db, item_id)

        if item.project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete priority item that has been converted to a project. Delete the project first."
            )

        db.delete(item)
        db.commit()

    @staticmethod
    def convert_to_project(
        db: Session,
        item_id: UUID,
        project_name: str,
        description: Optional[str] = None,
        budget: Optional[Decimal] = None,
        notes: Optional[str] = None
    ) -> Project:
        """
        Convert a priority item to a project

        Args:
            db: Database session
            item_id: Priority item ID to convert
            project_name: Name for the new project
            description: Optional project description
            budget: Optional project budget
            notes: Optional project notes

        Returns:
            Created Project object
        """
        item = PriorityItemService.get_priority_item(db, item_id)

        # Check if already converted
        if item.status == PriorityStatus.CONVERTED_TO_PROJECT.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Priority item has already been converted to a project"
            )

        # Create new project
        project = Project(
            project_name=project_name,
            description=description or item.description,
            status=ProjectStatus.PLANNED.value,
            budget=budget or item.cost,
            notes=notes
        )

        db.add(project)
        db.flush()  # Get project ID without committing

        # Update priority item
        item.project_id = project.id
        item.status = PriorityStatus.CONVERTED_TO_PROJECT.value
        item.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(project)

        return project
