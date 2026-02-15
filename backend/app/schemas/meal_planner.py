"""
Meal Planner Schemas
Pydantic models for recipes, ingredients, week plans, and shopping lists
"""

from datetime import date
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum


# Measurement units enum
class MeasurementUnit(str, Enum):
    """Common measurement units"""
    # Weight
    G = "g"
    KG = "kg"
    OZ = "oz"
    LB = "lb"
    # Volume
    ML = "ml"
    L = "L"
    TSP = "tsp"
    TBSP = "tbsp"
    CUP = "cup"
    # Count
    WHOLE = "whole"
    PIECE = "piece"
    CLOVE = "clove"
    BUNCH = "bunch"
    # Other
    TO_TASTE = "to taste"


# Ingredient schemas
class IngredientCreate(BaseModel):
    """Schema for creating an ingredient"""
    name: str = Field(..., min_length=1, max_length=255, description="Ingredient name")
    quantity_amount: Decimal = Field(..., gt=0, description="Numeric quantity")
    quantity_unit: MeasurementUnit = Field(..., description="Unit of measurement")
    sort_order: Optional[int] = Field(0, description="Display order in recipe")

    model_config = ConfigDict(from_attributes=True)


class IngredientResponse(BaseModel):
    """Schema for ingredient response"""
    id: str
    recipe_id: str
    name: str
    quantity_amount: str  # String for JSON serialization
    quantity_unit: str
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


# Recipe schemas
class RecipeCreate(BaseModel):
    """Schema for creating a recipe"""
    name: str = Field(..., min_length=1, max_length=255, description="Recipe name")
    steps: str = Field(..., min_length=1, description="Cooking instructions (HTML formatted)")
    ingredients: list[IngredientCreate] = Field(..., min_items=1, description="Recipe ingredients")

    model_config = ConfigDict(from_attributes=True)


class RecipeUpdate(BaseModel):
    """Schema for updating a recipe"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    steps: Optional[str] = Field(None, min_length=1)
    ingredients: Optional[list[IngredientCreate]] = None

    model_config = ConfigDict(from_attributes=True)


class RecipeResponse(BaseModel):
    """Schema for recipe response"""
    id: str
    name: str
    steps: str
    created_at: str
    updated_at: str
    ingredient_count: int

    model_config = ConfigDict(from_attributes=True)


class RecipeDetailResponse(BaseModel):
    """Schema for detailed recipe response with ingredients"""
    id: str
    name: str
    steps: str
    ingredients: list[IngredientResponse]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class RecipeListResponse(BaseModel):
    """Schema for list of recipes"""
    recipes: list[RecipeResponse]
    total: int


# Week Plan schemas
class WeekPlanCreate(BaseModel):
    """Schema for creating a week plan"""
    week_starting: date = Field(..., description="Monday of the week")
    monday_meal_id: Optional[UUID] = None
    tuesday_meal_id: Optional[UUID] = None
    wednesday_meal_id: Optional[UUID] = None
    thursday_meal_id: Optional[UUID] = None
    friday_meal_id: Optional[UUID] = None
    saturday_meal_id: Optional[UUID] = None
    sunday_meal_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class WeekPlanUpdate(BaseModel):
    """Schema for updating a week plan"""
    monday_meal_id: Optional[UUID] = None
    tuesday_meal_id: Optional[UUID] = None
    wednesday_meal_id: Optional[UUID] = None
    thursday_meal_id: Optional[UUID] = None
    friday_meal_id: Optional[UUID] = None
    saturday_meal_id: Optional[UUID] = None
    sunday_meal_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class WeekPlanResponse(BaseModel):
    """Schema for week plan response"""
    id: str
    week_starting: str
    monday_meal_id: Optional[str]
    tuesday_meal_id: Optional[str]
    wednesday_meal_id: Optional[str]
    thursday_meal_id: Optional[str]
    friday_meal_id: Optional[str]
    saturday_meal_id: Optional[str]
    sunday_meal_id: Optional[str]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class MealAssignment(BaseModel):
    """Schema for a meal assignment with recipe details"""
    day: str = Field(..., description="Day of week")
    meal_id: Optional[str]
    meal_name: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class WeekPlanDetailResponse(BaseModel):
    """Schema for detailed week plan with meal names"""
    id: str
    week_starting: str
    meals: list[MealAssignment]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


# Shopping List schemas
class ShoppingListItem(BaseModel):
    """Schema for a shopping list item"""
    ingredient: str = Field(..., description="Ingredient name")
    quantity: str = Field(..., description="Consolidated quantity")
    recipe_names: list[str] = Field(..., description="Recipes using this ingredient")

    model_config = ConfigDict(from_attributes=True)


class ShoppingListResponse(BaseModel):
    """Schema for shopping list response"""
    week_starting: str
    items: list[ShoppingListItem]
    total_items: int

    model_config = ConfigDict(from_attributes=True)
