import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Card } from '@/components/ui/card';
import { Save, Trash2, Eye } from 'lucide-react';
import { toast } from 'sonner';
import { format, startOfWeek } from 'date-fns';
import { mealPlannerService, type Recipe, type RecipeDetail, type WeekPlanDetail, type WeekPlanCreate } from '@/services/mealPlannerService';

const getErrorMessage = (error: any): string => {
  return error.response?.data?.detail || error.message || 'An error occurred';
};

// Map meal slots (1-7) to backend day fields
const MEAL_SLOTS = [
  { slot: 1, label: 'Meal 1', dayField: 'monday_meal_id' },
  { slot: 2, label: 'Meal 2', dayField: 'tuesday_meal_id' },
  { slot: 3, label: 'Meal 3', dayField: 'wednesday_meal_id' },
  { slot: 4, label: 'Meal 4', dayField: 'thursday_meal_id' },
  { slot: 5, label: 'Meal 5', dayField: 'friday_meal_id' },
  { slot: 6, label: 'Meal 6', dayField: 'saturday_meal_id' },
  { slot: 7, label: 'Meal 7', dayField: 'sunday_meal_id' },
];

export default function WeekPlanTab() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [weekPlan, setWeekPlan] = useState<WeekPlanDetail | null>(null);
  const [weekStarting, setWeekStarting] = useState('');
  const [loading, setLoading] = useState(false);

  // Meal selections (meal slot 1-7 -> recipe ID)
  const [mealSelections, setMealSelections] = useState<Record<number, string>>({});

  // View recipe dialog
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState<RecipeDetail | null>(null);

  useEffect(() => {
    loadRecipes();
    loadCurrentWeekPlan();
  }, []);

  const loadRecipes = async () => {
    try {
      const response = await mealPlannerService.recipes.list();
      setRecipes(response.recipes);
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    }
  };

  const loadCurrentWeekPlan = async () => {
    try {
      setLoading(true);
      const plan = await mealPlannerService.weekPlans.getCurrent();
      setWeekPlan(plan);
      setWeekStarting(plan.week_starting);

      // Extract meal selections from backend day fields
      const selections: Record<number, string> = {};
      MEAL_SLOTS.forEach((slot) => {
        const meal = plan.meals.find(m => m.day.toLowerCase() === slot.dayField.replace('_meal_id', ''));
        if (meal && meal.meal_id) {
          selections[slot.slot] = meal.meal_id;
        }
      });
      setMealSelections(selections);
    } catch (error: any) {
      // Week plan doesn't exist yet - that's okay
      setWeekPlan(null);
      setMealSelections({});
      // Calculate current week starting date for display
      const monday = startOfWeek(new Date(), { weekStartsOn: 1 });
      setWeekStarting(format(monday, 'yyyy-MM-dd'));
    } finally {
      setLoading(false);
    }
  };

  const handleMealChange = (slot: number, recipeId: string) => {
    if (recipeId === 'none') {
      const updated = { ...mealSelections };
      delete updated[slot];
      setMealSelections(updated);
    } else {
      setMealSelections({
        ...mealSelections,
        [slot]: recipeId,
      });
    }
  };

  const handleSave = async () => {
    try {
      // Calculate current week starting date
      const monday = startOfWeek(new Date(), { weekStartsOn: 1 });
      const weekStr = format(monday, 'yyyy-MM-dd');

      // Map meal slots back to backend day fields
      const data: any = {
        week_starting: weekStr,
      };

      MEAL_SLOTS.forEach((slot) => {
        data[slot.dayField] = mealSelections[slot.slot] || null;
      });

      await mealPlannerService.weekPlans.createOrUpdate(data as WeekPlanCreate);
      toast.success('Week plan saved successfully');
      loadCurrentWeekPlan();
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleDelete = async () => {
    if (!weekPlan) return;

    if (!confirm('Are you sure you want to delete this week plan?')) {
      return;
    }

    try {
      await mealPlannerService.weekPlans.delete();
      toast.success('Week plan deleted successfully');
      setWeekPlan(null);
      setMealSelections({});
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleClearAll = () => {
    setMealSelections({});
  };

  const handleViewRecipe = async (recipeId: string) => {
    try {
      const detail = await mealPlannerService.recipes.get(recipeId);
      setSelectedRecipe(detail);
      setIsViewDialogOpen(true);
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Current Week's Meal Plan</h3>
          <p className="text-sm text-muted-foreground">
            Week starting {weekStarting ? format(new Date(weekStarting), 'PPP') : '...'}
          </p>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={handleClearAll}>
            Clear All
          </Button>
          {weekPlan && (
            <Button variant="destructive" onClick={handleDelete}>
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Plan
            </Button>
          )}
        </div>
      </div>

      {/* Meal Planning Grid */}
      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading week plan...</div>
      ) : recipes.length === 0 ? (
        <Card className="p-8 text-center text-muted-foreground">
          <p>No recipes available. Create some recipes first!</p>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {MEAL_SLOTS.map((slot) => (
            <Card key={slot.slot} className="p-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label className="text-base font-semibold">{slot.label}</Label>
                  {mealSelections[slot.slot] && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleMealChange(slot.slot, 'none')}
                    >
                      Clear
                    </Button>
                  )}
                </div>

                <Select
                  value={mealSelections[slot.slot] || 'none'}
                  onValueChange={(value) => handleMealChange(slot.slot, value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a recipe" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No meal</SelectItem>
                    {recipes.map((recipe) => (
                      <SelectItem key={recipe.id} value={recipe.id}>
                        {recipe.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {mealSelections[slot.slot] && (
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      {recipes.find(r => r.id === mealSelections[slot.slot])?.ingredient_count || 0} ingredients
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleViewRecipe(mealSelections[slot.slot])}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave} size="lg">
          <Save className="h-4 w-4 mr-2" />
          Save Week Plan
        </Button>
      </div>

      {/* View Recipe Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={(open) => {
        if (!open) {
          setIsViewDialogOpen(false);
          setSelectedRecipe(null);
        }
      }}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-white dark:bg-white">
          <DialogHeader>
            <DialogTitle>{selectedRecipe?.name}</DialogTitle>
            <DialogDescription>
              Recipe details
            </DialogDescription>
          </DialogHeader>
          {selectedRecipe && (
            <div className="space-y-6">
              {/* Ingredients */}
              <div className="space-y-3">
                <h3 className="text-base font-semibold">Ingredients ({selectedRecipe.ingredients.length})</h3>
                <div className="space-y-2">
                  {selectedRecipe.ingredients.map((ingredient, index) => (
                    <div key={ingredient.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm font-medium text-gray-500 min-w-[20px]">{index + 1}.</span>
                      <div className="flex-1">
                        <span className="font-medium">{ingredient.name}</span>
                      </div>
                      <span className="text-sm text-gray-600">{ingredient.quantity_amount} {ingredient.quantity_unit}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Steps */}
              <div className="space-y-3">
                <h3 className="text-base font-semibold">Cooking Steps</h3>
                <div className="p-4 bg-gray-50 rounded-lg whitespace-pre-wrap text-sm">
                  {selectedRecipe.steps}
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsViewDialogOpen(false)}
            >
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
