import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Plus, Pencil, Trash2, Search, X, Eye } from 'lucide-react';
import { toast } from 'sonner';
import { mealPlannerService, type Recipe, type RecipeDetail, type IngredientCreate, type MeasurementUnit } from '@/services/mealPlannerService';

const getErrorMessage = (error: any): string => {
  return error.response?.data?.detail || error.message || 'An error occurred';
};

export default function RecipesTab() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState<RecipeDetail | null>(null);

  // Form state
  const [formName, setFormName] = useState('');
  const [formSteps, setFormSteps] = useState('');
  const [formIngredients, setFormIngredients] = useState<IngredientCreate[]>([
    { name: '', quantity_amount: 0, quantity_unit: 'g' }
  ]);

  const loadRecipes = async () => {
    try {
      setLoading(true);
      const response = await mealPlannerService.recipes.list(searchQuery || undefined);
      setRecipes(response.recipes);
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecipes();
  }, []);

  const handleSearch = () => {
    loadRecipes();
  };

  const resetForm = () => {
    setFormName('');
    setFormSteps('');
    setFormIngredients([{ name: '', quantity_amount: 0, quantity_unit: 'g' }]);
    setSelectedRecipe(null);
  };

  const addIngredient = () => {
    setFormIngredients([...formIngredients, { name: '', quantity_amount: 0, quantity_unit: 'g' }]);
  };

  const removeIngredient = (index: number) => {
    setFormIngredients(formIngredients.filter((_, i) => i !== index));
  };

  const updateIngredient = (index: number, field: 'name' | 'quantity_amount' | 'quantity_unit', value: string | number) => {
    const updated = [...formIngredients];
    if (field === 'name' || field === 'quantity_unit') {
      updated[index][field] = value as any;
    } else if (field === 'quantity_amount') {
      updated[index][field] = Number(value);
    }
    setFormIngredients(updated);
  };

  const openAddDialog = () => {
    resetForm();
    setIsAddDialogOpen(true);
  };

  const openViewDialog = async (recipe: Recipe) => {
    try {
      const detail = await mealPlannerService.recipes.get(recipe.id);
      setSelectedRecipe(detail);
      setIsViewDialogOpen(true);
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    }
  };

  const openEditDialog = async (recipe: Recipe) => {
    try {
      const detail = await mealPlannerService.recipes.get(recipe.id);
      setSelectedRecipe(detail);
      setFormName(detail.name);
      setFormSteps(detail.steps);
      setFormIngredients(
        detail.ingredients.length > 0
          ? detail.ingredients.map(ing => ({
              name: ing.name,
              quantity_amount: parseFloat(ing.quantity_amount),
              quantity_unit: ing.quantity_unit as MeasurementUnit
            }))
          : [{ name: '', quantity_amount: 0, quantity_unit: 'g' }]
      );
      setIsEditDialogOpen(true);
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate
    if (!formName.trim()) {
      toast.error('Recipe name is required');
      return;
    }

    if (!formSteps.trim()) {
      toast.error('Recipe steps are required');
      return;
    }

    const validIngredients = formIngredients.filter(ing => ing.name.trim() && ing.quantity_amount > 0);

    if (validIngredients.length === 0) {
      toast.error('At least one ingredient is required');
      return;
    }

    try {
      const data = {
        name: formName.trim(),
        steps: formSteps.trim(),
        ingredients: validIngredients.map((ing, idx) => ({
          name: ing.name.trim(),
          quantity_amount: ing.quantity_amount,
          quantity_unit: ing.quantity_unit,
          sort_order: idx,
        })),
      };

      if (selectedRecipe) {
        await mealPlannerService.recipes.update(selectedRecipe.id, data);
        toast.success('Recipe updated successfully');
        setIsEditDialogOpen(false);
      } else {
        await mealPlannerService.recipes.create(data);
        toast.success('Recipe created successfully');
        setIsAddDialogOpen(false);
      }

      resetForm();
      loadRecipes();
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleDelete = async (recipe: Recipe) => {
    if (!confirm(`Are you sure you want to delete "${recipe.name}"?`)) {
      return;
    }

    try {
      await mealPlannerService.recipes.delete(recipe.id);
      toast.success('Recipe deleted successfully');
      loadRecipes();
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    }
  };

  return (
    <div className="space-y-4">
      {/* Search and Add */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 flex gap-2">
          <Input
            placeholder="Search recipes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <Button onClick={handleSearch} variant="outline">
            <Search className="h-4 w-4" />
          </Button>
        </div>
        <Button onClick={openAddDialog}>
          <Plus className="h-4 w-4 mr-2" />
          Add Recipe
        </Button>
      </div>

      {/* Recipes Table */}
      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading recipes...</div>
      ) : recipes.length === 0 ? (
        <Card className="p-8 text-center text-muted-foreground">
          <p>No recipes found. Create your first recipe to get started!</p>
        </Card>
      ) : (
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Ingredients</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {recipes.map((recipe) => (
                <TableRow key={recipe.id}>
                  <TableCell className="font-medium">{recipe.name}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{recipe.ingredient_count} items</Badge>
                  </TableCell>
                  <TableCell>{new Date(recipe.created_at).toLocaleDateString()}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => openViewDialog(recipe)}
                        title="View recipe"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => openEditDialog(recipe)}
                        title="Edit recipe"
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(recipe)}
                        title="Delete recipe"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={isAddDialogOpen || isEditDialogOpen} onOpenChange={(open) => {
        if (!open) {
          setIsAddDialogOpen(false);
          setIsEditDialogOpen(false);
          resetForm();
        }
      }}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-white dark:bg-white">
          <DialogHeader>
            <DialogTitle>{selectedRecipe ? 'Edit Recipe' : 'Add Recipe'}</DialogTitle>
            <DialogDescription>
              {selectedRecipe ? 'Update the recipe details below' : 'Create a new recipe with ingredients and steps'}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Recipe Name */}
            <div className="space-y-2">
              <Label htmlFor="recipe-name">Recipe Name *</Label>
              <Input
                id="recipe-name"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="e.g., Spaghetti Bolognese"
                required
              />
            </div>

            {/* Ingredients */}
            <div className="space-y-3">
              <Label className="text-base font-semibold">Ingredients *</Label>
              <div className="space-y-3">
                {formIngredients.map((ingredient, index) => (
                  <div key={index} className="grid grid-cols-12 gap-3 items-start">
                    <div className="col-span-5">
                      <Label htmlFor={`ingredient-name-${index}`} className="text-xs text-muted-foreground mb-1 block">
                        Ingredient Name
                      </Label>
                      <Input
                        id={`ingredient-name-${index}`}
                        placeholder="e.g., Chicken breast, Onion"
                        value={ingredient.name}
                        onChange={(e) => updateIngredient(index, 'name', e.target.value)}
                        className="h-10"
                      />
                    </div>
                    <div className="col-span-2">
                      <Label htmlFor={`ingredient-amount-${index}`} className="text-xs text-muted-foreground mb-1 block">
                        Amount
                      </Label>
                      <Input
                        id={`ingredient-amount-${index}`}
                        type="number"
                        placeholder="300"
                        value={ingredient.quantity_amount || ''}
                        onChange={(e) => updateIngredient(index, 'quantity_amount', e.target.value)}
                        className="h-10"
                        min="0"
                        step="0.01"
                      />
                    </div>
                    <div className="col-span-4">
                      <Label htmlFor={`ingredient-unit-${index}`} className="text-xs text-muted-foreground mb-1 block">
                        Unit
                      </Label>
                      <Select
                        value={ingredient.quantity_unit}
                        onValueChange={(value) => updateIngredient(index, 'quantity_unit', value)}
                      >
                        <SelectTrigger id={`ingredient-unit-${index}`} className="h-10">
                          <SelectValue placeholder="Select unit" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="g">g (grams)</SelectItem>
                          <SelectItem value="kg">kg (kilograms)</SelectItem>
                          <SelectItem value="oz">oz (ounces)</SelectItem>
                          <SelectItem value="lb">lb (pounds)</SelectItem>
                          <SelectItem value="ml">ml (milliliters)</SelectItem>
                          <SelectItem value="L">L (liters)</SelectItem>
                          <SelectItem value="tsp">tsp (teaspoon)</SelectItem>
                          <SelectItem value="tbsp">tbsp (tablespoon)</SelectItem>
                          <SelectItem value="cup">cup</SelectItem>
                          <SelectItem value="whole">whole</SelectItem>
                          <SelectItem value="piece">piece</SelectItem>
                          <SelectItem value="clove">clove</SelectItem>
                          <SelectItem value="bunch">bunch</SelectItem>
                          <SelectItem value="to taste">to taste</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="col-span-1 flex items-end">
                      {formIngredients.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeIngredient(index)}
                          className="h-10 w-10"
                          title="Remove ingredient"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <Button type="button" variant="outline" size="sm" onClick={addIngredient}>
                <Plus className="h-4 w-4 mr-2" />
                Add Another Ingredient
              </Button>
            </div>

            {/* Steps */}
            <div className="space-y-2">
              <Label htmlFor="recipe-steps">Cooking Steps *</Label>
              <Textarea
                id="recipe-steps"
                value={formSteps}
                onChange={(e) => setFormSteps(e.target.value)}
                placeholder="Enter the cooking steps..."
                rows={8}
                required
              />
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setIsAddDialogOpen(false);
                  setIsEditDialogOpen(false);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button type="submit">
                {selectedRecipe ? 'Update Recipe' : 'Create Recipe'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

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
            <Button
              onClick={() => {
                setIsViewDialogOpen(false);
                if (selectedRecipe) {
                  openEditDialog(selectedRecipe as any);
                }
              }}
            >
              <Pencil className="h-4 w-4 mr-2" />
              Edit Recipe
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
