import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import RecipesTab from './RecipesTab';
import WeekPlanTab from './WeekPlanTab';
import ShoppingListTab from './ShoppingListTab';

export default function MealPlanner() {
  const [activeTab, setActiveTab] = useState('recipes');

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Meal Planner</h1>
        <p className="text-muted-foreground">
          Manage recipes, plan weekly meals, and generate shopping lists
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="recipes">Recipes</TabsTrigger>
          <TabsTrigger value="weekplan">Week Plan</TabsTrigger>
          <TabsTrigger value="shopping">Shopping List</TabsTrigger>
        </TabsList>

        <TabsContent value="recipes" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Recipe Collection</CardTitle>
              <CardDescription>
                Store and manage your favorite recipes with ingredients and steps
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RecipesTab />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="weekplan" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Weekly Meal Plan</CardTitle>
              <CardDescription>
                Plan meals for each day of the week using your recipe collection
              </CardDescription>
            </CardHeader>
            <CardContent>
              <WeekPlanTab />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="shopping" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Shopping List</CardTitle>
              <CardDescription>
                Auto-generated shopping list based on your weekly meal plan
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ShoppingListTab />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
