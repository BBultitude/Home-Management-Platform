"""
Meal Planner Service
Handles recipes, week plans, and shopping list generation
Ported from: https://github.com/BBultitude/Meal-Planner
"""

from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID
from collections import defaultdict
import re
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.recipe import Recipe, Ingredient
from app.models.week_plan import WeekPlan


class MealPlannerService:
    """Service for meal planning operations"""

    # Pantry staples that should be marked as "As needed" instead of quantified
    PANTRY_STAPLES = [
        "salt", "pepper", "oil", "olive oil", "vegetable oil", "butter",
        "flour", "sugar", "water", "milk"
    ]

    # Australian measurement conversions
    AUSTRALIAN_CONVERSIONS = {
        "cup": 250,  # 1 cup = 250g for most ingredients
        "cups": 250,
        "tablespoon": 15,  # 1 tablespoon = 15ml
        "tablespoons": 15,
        "tbsp": 15,
        "teaspoon": 5,  # 1 teaspoon = 5ml
        "teaspoons": 5,
        "tsp": 5,
    }

    # ===== Recipe Management =====

    @staticmethod
    def create_recipe(
        db: Session,
        name: str,
        steps: str,
        ingredients: list[dict]
    ) -> Recipe:
        """
        Create a new recipe with ingredients

        Args:
            db: Database session
            name: Recipe name
            steps: Cooking instructions (HTML formatted)
            ingredients: List of ingredient dicts with name, quantity, sort_order

        Returns:
            Created Recipe
        """
        recipe = Recipe(
            name=name,
            steps=steps
        )

        db.add(recipe)
        db.flush()  # Get recipe ID

        # Add ingredients
        for ing_data in ingredients:
            ingredient = Ingredient(
                recipe_id=recipe.id,
                name=ing_data["name"],
                quantity_amount=ing_data["quantity_amount"],
                quantity_unit=ing_data["quantity_unit"],
                sort_order=ing_data.get("sort_order", 0)
            )
            db.add(ingredient)

        db.commit()
        db.refresh(recipe)

        return recipe

    @staticmethod
    def get_recipe(db: Session, recipe_id: UUID) -> Recipe:
        """Get a recipe by ID"""
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found"
            )

        return recipe

    @staticmethod
    def list_recipes(
        db: Session,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Recipe]:
        """
        List recipes with optional search

        Args:
            db: Database session
            search: Optional search term (matches recipe name or ingredient name)
            limit: Maximum entries to return
            offset: Pagination offset

        Returns:
            List of Recipe objects
        """
        query = db.query(Recipe)

        if search:
            # Search in recipe name or ingredient names
            search_pattern = f"%{search}%"
            query = query.outerjoin(Recipe.ingredients).filter(
                (Recipe.name.ilike(search_pattern)) |
                (Ingredient.name.ilike(search_pattern))
            ).distinct()

        query = query.order_by(Recipe.name)
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_recipe(
        db: Session,
        recipe_id: UUID,
        name: Optional[str] = None,
        steps: Optional[str] = None,
        ingredients: Optional[list[dict]] = None
    ) -> Recipe:
        """Update a recipe"""
        recipe = MealPlannerService.get_recipe(db, recipe_id)

        if name is not None:
            recipe.name = name

        if steps is not None:
            recipe.steps = steps

        if ingredients is not None:
            # Delete existing ingredients
            db.query(Ingredient).filter(Ingredient.recipe_id == recipe_id).delete()

            # Add new ingredients
            for ing_data in ingredients:
                ingredient = Ingredient(
                    recipe_id=recipe.id,
                    name=ing_data["name"],
                    quantity_amount=ing_data["quantity_amount"],
                    quantity_unit=ing_data["quantity_unit"],
                    sort_order=ing_data.get("sort_order", 0)
                )
                db.add(ingredient)

        recipe.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(recipe)

        return recipe

    @staticmethod
    def delete_recipe(db: Session, recipe_id: UUID) -> None:
        """Delete a recipe (cascade deletes ingredients)"""
        recipe = MealPlannerService.get_recipe(db, recipe_id)

        # Check if recipe is used in any week plans
        week_plans = db.query(WeekPlan).filter(
            (WeekPlan.monday_meal_id == recipe_id) |
            (WeekPlan.tuesday_meal_id == recipe_id) |
            (WeekPlan.wednesday_meal_id == recipe_id) |
            (WeekPlan.thursday_meal_id == recipe_id) |
            (WeekPlan.friday_meal_id == recipe_id) |
            (WeekPlan.saturday_meal_id == recipe_id) |
            (WeekPlan.sunday_meal_id == recipe_id)
        ).first()

        if week_plans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete recipe that is assigned to a week plan. Remove from week plans first."
            )

        db.delete(recipe)
        db.commit()

    # ===== Week Plan Management =====

    @staticmethod
    def create_week_plan(
        db: Session,
        week_starting: date,
        meal_ids: dict[str, Optional[UUID]]
    ) -> WeekPlan:
        """
        Create a new week plan

        Args:
            db: Database session
            week_starting: Monday of the week
            meal_ids: Dict with keys like monday_meal_id, tuesday_meal_id, etc.

        Returns:
            Created WeekPlan
        """
        # Ensure week_starting is a Monday
        if week_starting.weekday() != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="week_starting must be a Monday"
            )

        # Check if week plan already exists
        existing = db.query(WeekPlan).filter(WeekPlan.week_starting == week_starting).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Week plan for {week_starting} already exists"
            )

        week_plan = WeekPlan(
            week_starting=week_starting,
            **meal_ids
        )

        db.add(week_plan)
        db.commit()
        db.refresh(week_plan)

        return week_plan

    @staticmethod
    def get_week_plan(db: Session, plan_id: UUID) -> WeekPlan:
        """Get a week plan by ID"""
        plan = db.query(WeekPlan).filter(WeekPlan.id == plan_id).first()

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Week plan not found"
            )

        return plan

    @staticmethod
    def get_week_plan_by_date(db: Session, target_date: date) -> Optional[WeekPlan]:
        """Get week plan for the week containing target_date"""
        # Get Monday of the week
        monday = WeekPlan.get_monday_of_week(target_date)

        return db.query(WeekPlan).filter(WeekPlan.week_starting == monday).first()

    @staticmethod
    def get_current_week_plan(db: Session) -> Optional[WeekPlan]:
        """Get week plan for current week"""
        today = date.today()
        return MealPlannerService.get_week_plan_by_date(db, today)

    @staticmethod
    def update_week_plan(
        db: Session,
        plan_id: UUID,
        meal_ids: dict[str, Optional[UUID]]
    ) -> WeekPlan:
        """Update a week plan"""
        plan = MealPlannerService.get_week_plan(db, plan_id)

        # Update meal IDs
        for day, meal_id in meal_ids.items():
            if hasattr(plan, day):
                setattr(plan, day, meal_id)

        plan.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(plan)

        return plan

    @staticmethod
    def delete_week_plan(db: Session, plan_id: UUID) -> None:
        """Delete a week plan"""
        plan = MealPlannerService.get_week_plan(db, plan_id)

        db.delete(plan)
        db.commit()

    # ===== Shopping List Generation =====

    @staticmethod
    def _consolidate_ingredients(ingredients: list[tuple[str, float, str, str]]) -> dict[str, dict]:
        """
        Consolidate duplicate ingredients across recipes

        Args:
            ingredients: List of (ingredient_name, quantity_amount, quantity_unit, recipe_name) tuples

        Returns:
            Dict mapping ingredient_name to {quantity: str, recipes: list[str]}
        """
        # Group by (normalized_name, unit)
        groups = defaultdict(lambda: {"amount": 0.0, "unit": "", "recipes": []})

        for ing_name, amount, unit, recipe_name in ingredients:
            ing_lower = ing_name.lower()

            # Check if it's a pantry staple
            is_staple = any(staple in ing_lower for staple in MealPlannerService.PANTRY_STAPLES)

            # Use (normalized name, unit) as key for grouping
            # This ensures "Chicken" and "chicken" with same unit are combined
            key = (ing_lower, unit.lower() if not is_staple else "staple")

            if is_staple:
                groups[key]["amount"] = 0  # Don't accumulate pantry staples
                groups[key]["unit"] = "As needed"
                groups[key]["name"] = ing_name  # Keep original name
            else:
                groups[key]["amount"] += amount
                groups[key]["unit"] = unit
                groups[key]["name"] = ing_name  # Keep first occurrence name

            if recipe_name not in groups[key]["recipes"]:
                groups[key]["recipes"].append(recipe_name)

        # Convert grouped data to result format
        result = {}
        for (_, _), data in groups.items():
            ing_name = data["name"]
            unit = data["unit"]
            amount = data["amount"]
            recipes = data["recipes"]

            if unit == "As needed":
                quantity_str = "As needed"
            else:
                # Format amount nicely (remove trailing zeros)
                amount_str = f"{amount:.2f}".rstrip('0').rstrip('.')
                quantity_str = f"{amount_str} {unit}"

            result[ing_name] = {
                "quantity": quantity_str,
                "recipes": recipes
            }

        return result

    @staticmethod
    def generate_shopping_list(db: Session, plan_id: UUID) -> dict:
        """
        Generate shopping list from week plan

        Args:
            db: Database session
            plan_id: Week plan ID

        Returns:
            Dictionary with shopping list items
        """
        plan = MealPlannerService.get_week_plan(db, plan_id)

        # Collect all meal IDs from the week
        meal_ids = [
            plan.monday_meal_id, plan.tuesday_meal_id, plan.wednesday_meal_id,
            plan.thursday_meal_id, plan.friday_meal_id, plan.saturday_meal_id,
            plan.sunday_meal_id
        ]
        meal_ids = [m for m in meal_ids if m is not None]

        if not meal_ids:
            return {
                "week_starting": plan.week_starting.isoformat(),
                "items": [],
                "total_items": 0
            }

        # Fetch all recipes with ingredients
        recipes = db.query(Recipe).filter(Recipe.id.in_(meal_ids)).all()

        # Collect all ingredients with recipe names
        all_ingredients = []
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                all_ingredients.append((
                    ingredient.name,
                    float(ingredient.quantity_amount),
                    ingredient.quantity_unit,
                    recipe.name
                ))

        # Consolidate ingredients
        consolidated = MealPlannerService._consolidate_ingredients(all_ingredients)

        # Format for response
        items = [
            {
                "ingredient": ing_name,
                "quantity": data["quantity"],
                "recipe_names": data["recipes"]
            }
            for ing_name, data in sorted(consolidated.items())
        ]

        return {
            "week_starting": plan.week_starting.isoformat(),
            "items": items,
            "total_items": len(items)
        }
