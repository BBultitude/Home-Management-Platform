"""
Project Service
Handles CRUD operations for home improvement projects
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.project import Project, ProjectStatus


class ProjectService:
    """Service for project operations"""

    @staticmethod
    def create_project(
        db: Session,
        project_name: str,
        description: Optional[str] = None,
        priority_item_id: Optional[UUID] = None,
        project_status: ProjectStatus = ProjectStatus.PLANNED,
        start_date: Optional[date] = None,
        completion_date: Optional[date] = None,
        budget: Optional[Decimal] = None,
        actual_cost: Optional[Decimal] = None,
        notes: Optional[str] = None
    ) -> Project:
        """Create a new project"""
        if start_date and completion_date and completion_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completion date cannot be before start date"
            )

        project = Project(
            project_name=project_name,
            description=description,
            priority_item_id=priority_item_id,
            status=project_status.value,
            start_date=start_date,
            completion_date=completion_date,
            budget=budget,
            actual_cost=actual_cost,
            notes=notes
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def get_project(db: Session, project_id: UUID) -> Project:
        """Get a project by ID"""
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        return project

    @staticmethod
    def list_projects(
        db: Session,
        status_filter: Optional[ProjectStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Project]:
        """List projects with optional status filter"""
        query = db.query(Project)

        if status_filter:
            query = query.filter(Project.status == status_filter.value)

        query = query.order_by(Project.created_at.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_project(
        db: Session,
        project_id: UUID,
        project_name: Optional[str] = None,
        description: Optional[str] = None,
        project_status: Optional[ProjectStatus] = None,
        start_date: Optional[date] = None,
        completion_date: Optional[date] = None,
        budget: Optional[Decimal] = None,
        actual_cost: Optional[Decimal] = None,
        notes: Optional[str] = None
    ) -> Project:
        """Update a project"""
        project = ProjectService.get_project(db, project_id)

        if project_name is not None:
            project.project_name = project_name

        if description is not None:
            project.description = description

        if project_status is not None:
            project.status = project_status.value

        if start_date is not None:
            project.start_date = start_date

        if completion_date is not None:
            project.completion_date = completion_date

        # Validate date logic
        if project.start_date and project.completion_date:
            if project.completion_date < project.start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Completion date cannot be before start date"
                )

        if budget is not None:
            project.budget = budget

        if actual_cost is not None:
            project.actual_cost = actual_cost

        if notes is not None:
            project.notes = notes

        project.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def delete_project(db: Session, project_id: UUID) -> None:
        """
        Delete a project (cascade deletes quotes)

        Note: This will also unlink the associated priority_item if one exists
        """
        project = ProjectService.get_project(db, project_id)

        # Unlink from priority item if exists
        if project.priority_item_id:
            from app.models.priority_item import PriorityItem, PriorityStatus
            priority_item = db.query(PriorityItem).filter(
                PriorityItem.id == project.priority_item_id
            ).first()
            if priority_item:
                priority_item.project_id = None
                priority_item.status = PriorityStatus.PENDING.value

        db.delete(project)
        db.commit()

    @staticmethod
    def get_project_summary(db: Session) -> dict:
        """
        Get project summary statistics

        Returns:
            Dictionary with counts by status and budget totals
        """
        projects = db.query(Project).all()

        summary = {
            "total_projects": len(projects),
            "by_status": {},
            "total_budget": 0.0,
            "total_actual_cost": 0.0
        }

        # Initialize status counts
        for status in ProjectStatus:
            summary["by_status"][status.value] = 0

        # Calculate totals
        for project in projects:
            summary["by_status"][project.status] += 1
            if project.budget:
                summary["total_budget"] += float(project.budget)
            if project.actual_cost:
                summary["total_actual_cost"] += float(project.actual_cost)

        return summary
