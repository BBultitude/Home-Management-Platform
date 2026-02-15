"""
Meal Planner API endpoints
Handles recipes, weekly meal planning, and shopping list generation
Ported from: https://github.com/BBultitude/Meal-Planner
"""

from typing import Optional
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.services.meal_planner_service import MealPlannerService
from app.schemas.meal_planner import (
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RecipeDetailResponse,
    RecipeListResponse,
    IngredientResponse,
    WeekPlanCreate,
    WeekPlanUpdate,
    WeekPlanResponse,
    WeekPlanDetailResponse,
    MealAssignment,
    ShoppingListResponse,
    ShoppingListItem
)


router = APIRouter(prefix="/meals", tags=["meals"])


# Recipes
@router.post("/recipes", response_model=RecipeDetailResponse)
async def create_recipe(
    recipe_data: RecipeCreate,
    current_user: User = Depends(require_permission("meals:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new recipe with ingredients

    Requires permission: meals:write
    """
    ingredients_data = [
        {
            "name": ing.name,
            "quantity_amount": ing.quantity_amount,
            "quantity_unit": ing.quantity_unit,
            "sort_order": ing.sort_order
        }
        for ing in recipe_data.ingredients
    ]

    recipe = MealPlannerService.create_recipe(
        db=db,
        name=recipe_data.name,
        steps=recipe_data.steps,
        ingredients=ingredients_data
    )

    return RecipeDetailResponse(
        id=str(recipe.id),
        name=recipe.name,
        steps=recipe.steps,
        ingredients=[IngredientResponse(**ing.to_dict()) for ing in recipe.ingredients],
        created_at=recipe.created_at.isoformat(),
        updated_at=recipe.updated_at.isoformat()
    )


@router.get("/recipes", response_model=RecipeListResponse)
async def list_recipes(
    search: Optional[str] = Query(None, description="Search by recipe or ingredient name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List recipes with optional search

    Searches in recipe names and ingredient names
    """
    recipes = MealPlannerService.list_recipes(
        db=db,
        search=search,
        limit=limit,
        offset=offset
    )

    recipe_responses = [RecipeResponse(**r.to_dict()) for r in recipes]

    return RecipeListResponse(
        recipes=recipe_responses,
        total=len(recipes)
    )


@router.get("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
async def get_recipe(
    recipe_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific recipe with ingredients"""
    recipe = MealPlannerService.get_recipe(db, recipe_id)

    return RecipeDetailResponse(
        id=str(recipe.id),
        name=recipe.name,
        steps=recipe.steps,
        ingredients=[IngredientResponse(**ing.to_dict()) for ing in recipe.ingredients],
        created_at=recipe.created_at.isoformat(),
        updated_at=recipe.updated_at.isoformat()
    )


@router.put("/recipes/{recipe_id}", response_model=RecipeDetailResponse)
async def update_recipe(
    recipe_id: UUID,
    recipe_data: RecipeUpdate,
    current_user: User = Depends(require_permission("meals:write")),
    db: Session = Depends(get_db)
):
    """Update a recipe"""
    ingredients_data = None
    if recipe_data.ingredients:
        ingredients_data = [
            {
                "name": ing.name,
                "quantity_amount": ing.quantity_amount,
                "quantity_unit": ing.quantity_unit,
                "sort_order": ing.sort_order
            }
            for ing in recipe_data.ingredients
        ]

    recipe = MealPlannerService.update_recipe(
        db=db,
        recipe_id=recipe_id,
        name=recipe_data.name,
        steps=recipe_data.steps,
        ingredients=ingredients_data
    )

    return RecipeDetailResponse(
        id=str(recipe.id),
        name=recipe.name,
        steps=recipe.steps,
        ingredients=[IngredientResponse(**ing.to_dict()) for ing in recipe.ingredients],
        created_at=recipe.created_at.isoformat(),
        updated_at=recipe.updated_at.isoformat()
    )


@router.delete("/recipes/{recipe_id}")
async def delete_recipe(
    recipe_id: UUID,
    current_user: User = Depends(require_permission("meals:write")),
    db: Session = Depends(get_db)
):
    """Delete a recipe (cannot delete if assigned to a week plan)"""
    MealPlannerService.delete_recipe(db, recipe_id)

    return {"message": "Recipe deleted successfully", "id": str(recipe_id)}


# Week Plans
@router.post("/week-plans", response_model=WeekPlanResponse)
async def create_week_plan(
    plan_data: WeekPlanCreate,
    current_user: User = Depends(require_permission("meals:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new weekly meal plan

    week_starting must be a Monday

    Requires permission: meals:write
    """
    meal_ids = {
        "monday_meal_id": plan_data.monday_meal_id,
        "tuesday_meal_id": plan_data.tuesday_meal_id,
        "wednesday_meal_id": plan_data.wednesday_meal_id,
        "thursday_meal_id": plan_data.thursday_meal_id,
        "friday_meal_id": plan_data.friday_meal_id,
        "saturday_meal_id": plan_data.saturday_meal_id,
        "sunday_meal_id": plan_data.sunday_meal_id,
    }

    plan = MealPlannerService.create_week_plan(
        db=db,
        week_starting=plan_data.week_starting,
        meal_ids=meal_ids
    )

    return WeekPlanResponse(**plan.to_dict())


@router.get("/week-plans/current", response_model=WeekPlanDetailResponse)
async def get_current_week_plan(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get week plan for current week

    Returns detailed view with meal names
    """
    plan = MealPlannerService.get_current_week_plan(db)

    if not plan:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No meal plan for current week")

    # Build meal assignments with names
    meals = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i, day in enumerate(days):
        day_attr = f"{day.lower()}_meal_id"
        meal_id = getattr(plan, day_attr)

        meal_name = None
        if meal_id:
            meal_attr = f"{day.lower()}_meal"
            meal = getattr(plan, meal_attr)
            if meal:
                meal_name = meal.name

        meals.append(MealAssignment(
            day=day,
            meal_id=str(meal_id) if meal_id else None,
            meal_name=meal_name
        ))

    return WeekPlanDetailResponse(
        id=str(plan.id),
        week_starting=plan.week_starting.isoformat(),
        meals=meals,
        created_at=plan.created_at.isoformat(),
        updated_at=plan.updated_at.isoformat()
    )


@router.get("/week-plans/by-date/{target_date}", response_model=WeekPlanDetailResponse)
async def get_week_plan_by_date(
    target_date: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get week plan for the week containing target_date"""
    plan = MealPlannerService.get_week_plan_by_date(db, target_date)

    if not plan:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"No meal plan for week containing {target_date}")

    # Build meal assignments with names
    meals = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i, day in enumerate(days):
        day_attr = f"{day.lower()}_meal_id"
        meal_id = getattr(plan, day_attr)

        meal_name = None
        if meal_id:
            meal_attr = f"{day.lower()}_meal"
            meal = getattr(plan, meal_attr)
            if meal:
                meal_name = meal.name

        meals.append(MealAssignment(
            day=day,
            meal_id=str(meal_id) if meal_id else None,
            meal_name=meal_name
        ))

    return WeekPlanDetailResponse(
        id=str(plan.id),
        week_starting=plan.week_starting.isoformat(),
        meals=meals,
        created_at=plan.created_at.isoformat(),
        updated_at=plan.updated_at.isoformat()
    )


@router.get("/week-plans/{plan_id}", response_model=WeekPlanResponse)
async def get_week_plan(
    plan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific week plan"""
    plan = MealPlannerService.get_week_plan(db, plan_id)

    return WeekPlanResponse(**plan.to_dict())


@router.put("/week-plans/{plan_id}", response_model=WeekPlanResponse)
async def update_week_plan(
    plan_id: UUID,
    plan_data: WeekPlanUpdate,
    current_user: User = Depends(require_permission("meals:write")),
    db: Session = Depends(get_db)
):
    """Update a week plan"""
    meal_ids = {}
    if plan_data.monday_meal_id is not None:
        meal_ids["monday_meal_id"] = plan_data.monday_meal_id
    if plan_data.tuesday_meal_id is not None:
        meal_ids["tuesday_meal_id"] = plan_data.tuesday_meal_id
    if plan_data.wednesday_meal_id is not None:
        meal_ids["wednesday_meal_id"] = plan_data.wednesday_meal_id
    if plan_data.thursday_meal_id is not None:
        meal_ids["thursday_meal_id"] = plan_data.thursday_meal_id
    if plan_data.friday_meal_id is not None:
        meal_ids["friday_meal_id"] = plan_data.friday_meal_id
    if plan_data.saturday_meal_id is not None:
        meal_ids["saturday_meal_id"] = plan_data.saturday_meal_id
    if plan_data.sunday_meal_id is not None:
        meal_ids["sunday_meal_id"] = plan_data.sunday_meal_id

    plan = MealPlannerService.update_week_plan(
        db=db,
        plan_id=plan_id,
        meal_ids=meal_ids
    )

    return WeekPlanResponse(**plan.to_dict())


@router.delete("/week-plans/{plan_id}")
async def delete_week_plan(
    plan_id: UUID,
    current_user: User = Depends(require_permission("meals:write")),
    db: Session = Depends(get_db)
):
    """Delete a week plan"""
    MealPlannerService.delete_week_plan(db, plan_id)

    return {"message": "Week plan deleted successfully", "id": str(plan_id)}


# Shopping List
@router.get("/week-plans/{plan_id}/shopping-list", response_model=ShoppingListResponse)
async def generate_shopping_list(
    plan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate shopping list from week plan

    Automatically consolidates duplicate ingredients across recipes.
    Pantry staples (salt, pepper, oil, etc.) are marked as "As needed".
    """
    result = MealPlannerService.generate_shopping_list(db, plan_id)

    return ShoppingListResponse(
        week_starting=result["week_starting"],
        items=[ShoppingListItem(**item) for item in result["items"]],
        total_items=result["total_items"]
    )
