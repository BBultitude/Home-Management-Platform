import { apiClient } from '@/lib/api';

// Measurement units enum matching backend
export type MeasurementUnit =
  | 'g' | 'kg' | 'oz' | 'lb'  // Weight
  | 'ml' | 'L' | 'tsp' | 'tbsp' | 'cup'  // Volume
  | 'whole' | 'piece' | 'clove' | 'bunch'  // Count
  | 'to taste';  // Other

// Recipe interfaces
export interface Ingredient {
  id: string;
  recipe_id: string;
  name: string;
  quantity_amount: string;  // String representation of Decimal
  quantity_unit: string;
  sort_order: number;
}

export interface IngredientCreate {
  name: string;
  quantity_amount: number;
  quantity_unit: MeasurementUnit;
  sort_order?: number;
}

export interface Recipe {
  id: string;
  name: string;
  steps: string;
  created_at: string;
  updated_at: string;
  ingredient_count: number;
}

export interface RecipeDetail {
  id: string;
  name: string;
  steps: string;
  ingredients: Ingredient[];
  created_at: string;
  updated_at: string;
}

export interface RecipeCreate {
  name: string;
  steps: string;
  ingredients: IngredientCreate[];
}

export interface RecipeUpdate {
  name?: string;
  steps?: string;
  ingredients?: IngredientCreate[];
}

export interface RecipeListResponse {
  recipes: Recipe[];
  total: number;
}

// Week Plan interfaces
export interface WeekPlan {
  id: string;
  week_starting: string;
  monday_meal_id: string | null;
  tuesday_meal_id: string | null;
  wednesday_meal_id: string | null;
  thursday_meal_id: string | null;
  friday_meal_id: string | null;
  saturday_meal_id: string | null;
  sunday_meal_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface MealAssignment {
  day: string;
  meal_id: string | null;
  meal_name: string | null;
}

export interface WeekPlanDetail {
  id: string;
  week_starting: string;
  meals: MealAssignment[];
  created_at: string;
  updated_at: string;
}

export interface WeekPlanCreate {
  week_starting: string;
  monday_meal_id?: string;
  tuesday_meal_id?: string;
  wednesday_meal_id?: string;
  thursday_meal_id?: string;
  friday_meal_id?: string;
  saturday_meal_id?: string;
  sunday_meal_id?: string;
}

export interface WeekPlanUpdate {
  monday_meal_id?: string | null;
  tuesday_meal_id?: string | null;
  wednesday_meal_id?: string | null;
  thursday_meal_id?: string | null;
  friday_meal_id?: string | null;
  saturday_meal_id?: string | null;
  sunday_meal_id?: string | null;
}

// Shopping List interfaces
export interface ShoppingListItem {
  ingredient: string;
  quantity: string;
  recipe_names: string[];
}

export interface ShoppingListResponse {
  week_starting: string;
  items: ShoppingListItem[];
  total_items: number;
}

export const mealPlannerService = {
  // Recipe endpoints
  recipes: {
    list: async (search?: string, limit?: number, offset?: number): Promise<RecipeListResponse> => {
      return await apiClient.get('/meals/recipes', {
        params: { search, limit, offset },
      }) as RecipeListResponse;
    },

    get: async (id: string): Promise<RecipeDetail> => {
      return await apiClient.get(`/meals/recipes/${id}`) as RecipeDetail;
    },

    create: async (data: RecipeCreate): Promise<RecipeDetail> => {
      return await apiClient.post('/meals/recipes', data) as RecipeDetail;
    },

    update: async (id: string, data: RecipeUpdate): Promise<RecipeDetail> => {
      return await apiClient.put(`/meals/recipes/${id}`, data) as RecipeDetail;
    },

    delete: async (id: string): Promise<{ message: string; id: string }> => {
      return await apiClient.delete(`/meals/recipes/${id}`) as { message: string; id: string };
    },
  },

  // Week Plan endpoints
  weekPlans: {
    getCurrent: async (): Promise<WeekPlanDetail> => {
      return await apiClient.get('/meals/week-plans/current') as WeekPlanDetail;
    },

    createOrUpdate: async (data: WeekPlanCreate): Promise<WeekPlanDetail> => {
      // Try to update first, if it fails (404), then create
      try {
        const current = await apiClient.get('/meals/week-plans/current') as WeekPlanDetail;
        // Week plan exists, update it
        return await apiClient.put(`/meals/week-plans/${current.id}`, data) as WeekPlanDetail;
      } catch (error: any) {
        // Week plan doesn't exist, create it
        console.error(error);
        return await apiClient.post('/meals/week-plans', data) as WeekPlanDetail;
      }
    },

    delete: async (): Promise<{ message: string }> => {
      const current = await apiClient.get('/meals/week-plans/current') as WeekPlanDetail;
      return await apiClient.delete(`/meals/week-plans/${current.id}`) as { message: string };
    },
  },

  // Shopping List endpoint
  shoppingList: {
    getCurrent: async (): Promise<ShoppingListResponse> => {
      // First get the current week plan to get its ID
      const plan = await apiClient.get('/meals/week-plans/current') as WeekPlanDetail;
      // Then get the shopping list for that plan
      return await apiClient.get(`/meals/week-plans/${plan.id}/shopping-list`) as ShoppingListResponse;
    },
  },
};
