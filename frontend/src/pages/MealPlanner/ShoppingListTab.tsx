import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Download, ShoppingCart } from 'lucide-react';
import { toast } from 'sonner';
import { format } from 'date-fns';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { mealPlannerService, type ShoppingListResponse, type ShoppingListItem } from '@/services/mealPlannerService';

export default function ShoppingListTab() {
  const [shoppingList, setShoppingList] = useState<ShoppingListResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCurrentShoppingList();
  }, []);

  const loadCurrentShoppingList = async () => {
    try {
      setLoading(true);
      const list = await mealPlannerService.shoppingList.getCurrent();
      setShoppingList(list);
    } catch (error: any) {
      // Shopping list doesn't exist for this week - that's okay
      setShoppingList(null);
      if (error.response?.status !== 404) {
        // Only show error if it's not a "not found" error
        // (not found just means no week plan exists yet)
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!shoppingList || shoppingList.items.length === 0) return;

    // Create plain text shopping list
    let text = `Shopping List - Week of ${format(new Date(shoppingList.week_starting), 'PPP')}\n\n`;

    shoppingList.items.forEach((item: ShoppingListItem, index: number) => {
      text += `${index + 1}. ${item.ingredient} - ${item.quantity}\n`;
      if (item.recipe_names.length > 0) {
        text += `   (Used in: ${item.recipe_names.join(', ')})\n`;
      }
      text += '\n';
    });

    text += `\nTotal Items: ${shoppingList.total_items}`;

    // Create and download file
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `shopping-list-${shoppingList.week_starting}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast.success('Shopping list downloaded');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      {shoppingList && shoppingList.items.length > 0 && (
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-end">
          <Button onClick={handleDownload}>
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
        </div>
      )}

      {/* Shopping List */}
      {loading ? (
        <div className="text-center py-8 text-muted-foreground">Loading shopping list...</div>
      ) : !shoppingList || shoppingList.items.length === 0 ? (
        <Card className="p-8 text-center text-muted-foreground">
          <ShoppingCart className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium mb-2">No Shopping List Available</p>
          <p className="text-sm">
            Create a week plan with recipes to generate a shopping list
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Summary */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">
                Shopping List for Week of {format(new Date(shoppingList.week_starting), 'PPP')}
              </h3>
              <p className="text-sm text-muted-foreground">
                Auto-generated from your weekly meal plan
              </p>
            </div>
            <Badge variant="secondary" className="text-base px-4 py-2">
              {shoppingList.total_items} {shoppingList.total_items === 1 ? 'item' : 'items'}
            </Badge>
          </div>

          {/* Items Table */}
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Ingredient</TableHead>
                  <TableHead>Quantity</TableHead>
                  <TableHead>Used In</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {shoppingList.items.map((item: ShoppingListItem, index: number) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell>{item.ingredient}</TableCell>
                    <TableCell>{item.quantity}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {item.recipe_names.map((recipeName: string, idx: number) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {recipeName}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      )}
    </div>
  );
}
