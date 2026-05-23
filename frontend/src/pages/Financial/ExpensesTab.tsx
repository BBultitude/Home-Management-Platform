import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/common/EmptyState';
import { PageLoader } from '@/components/common/PageLoader';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { LoadingButton } from '@/components/ui/loading-button';
import { financialService } from '@/services/financialService';
import type {
  ExpenseCategory,
  ExpenseCategoryCreate,
  Expense,
  ExpenseCreate,
  ExpenseFrequency,
  BankAccount
} from '@/services/financialService';
import { getErrorMessage } from '@/lib/errorMessages';
import { toast } from 'sonner';
import { normalizeToMonthly, formatCurrency, formatFrequency } from '@/lib/frequencyUtils';

export function ExpensesTab() {
  // Data state
  const [categories, setCategories] = useState<ExpenseCategory[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);

  // Category dialog state
  const [showCategoryDialog, setShowCategoryDialog] = useState(false);
  const [editingCategory, setEditingCategory] = useState<ExpenseCategory | null>(null);
  const [deleteCategory, setDeleteCategory] = useState<ExpenseCategory | null>(null);
  const [submittingCategory, setSubmittingCategory] = useState(false);

  // Expense dialog state
  const [showExpenseDialog, setShowExpenseDialog] = useState(false);
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);
  const [deleteExpense, setDeleteExpense] = useState<Expense | null>(null);
  const [submittingExpense, setSubmittingExpense] = useState(false);

  // Category form state
  const [formCategoryName, setFormCategoryName] = useState('');
  const [formBankAccountId, setFormBankAccountId] = useState('');
  const [formColor, setFormColor] = useState('#3B82F6');

  // Expense form state
  const [formExpenseName, setFormExpenseName] = useState('');
  const [formAmount, setFormAmount] = useState('');
  const [formFrequency, setFormFrequency] = useState<ExpenseFrequency>('monthly');
  const [formCategoryId, setFormCategoryId] = useState('');
  const [formNotes, setFormNotes] = useState('');

  // Filter state
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState<string>('all');

  // Summary stats
  const filteredExpenses = selectedCategoryFilter === 'all'
    ? expenses
    : expenses.filter(e => e.category_id.toString() === selectedCategoryFilter);

  const totalMonthlyExpenses = filteredExpenses.reduce(
    (sum, e) => sum + normalizeToMonthly(e.amount, e.frequency),
    0
  );

  // Fetch all data
  const fetchData = async () => {
    setLoading(true);
    try {
      const [categoriesResp, expensesResp, accountsResp] = await Promise.all([
        financialService.categories.list(),
        financialService.expenses.list(),
        financialService.accounts.list(),
      ]);
      setCategories(categoriesResp.categories);
      setExpenses(expensesResp.expenses);
      setAccounts(accountsResp.accounts);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Category handlers
  const handleOpenCategoryDialog = (category?: ExpenseCategory) => {
    if (category) {
      setEditingCategory(category);
      setFormCategoryName(category.category_name);
      setFormBankAccountId(category.bank_account_id.toString());
      setFormColor(category.color || '#3B82F6');
    } else {
      setEditingCategory(null);
      setFormCategoryName('');
      setFormBankAccountId('');
      setFormColor('#3B82F6');
    }
    setShowCategoryDialog(true);
  };

  const handleCloseCategoryDialog = () => {
    setShowCategoryDialog(false);
    setEditingCategory(null);
    setFormCategoryName('');
    setFormBankAccountId('');
    setFormColor('#3B82F6');
  };

  const handleSubmitCategory = async () => {
    if (!formCategoryName || !formBankAccountId) {
      toast.error('Please fill in all required fields');
      return;
    }

    setSubmittingCategory(true);
    try {
      if (editingCategory) {
        await financialService.categories.update(editingCategory.id, {
          category_name: formCategoryName,
          bank_account_id: Number.parseInt(formBankAccountId),
          color: formColor,
        });
        toast.success('Category updated');
      } else {
        const data: ExpenseCategoryCreate = {
          category_name: formCategoryName,
          bank_account_id: Number.parseInt(formBankAccountId),
          color: formColor,
        };
        await financialService.categories.create(data);
        toast.success('Category created');
      }
      handleCloseCategoryDialog();
      fetchData();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSubmittingCategory(false);
    }
  };

  const handleDeleteCategory = async () => {
    if (!deleteCategory) return;

    try {
      await financialService.categories.delete(deleteCategory.id);
      toast.success('Category deleted');
      setDeleteCategory(null);
      fetchData();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  // Expense handlers
  const handleOpenExpenseDialog = (expense?: Expense) => {
    if (expense) {
      setEditingExpense(expense);
      setFormExpenseName(expense.expense_name);
      setFormAmount(expense.amount.toString());
      setFormFrequency(expense.frequency);
      setFormCategoryId(expense.category_id.toString());
      setFormNotes(expense.notes || '');
    } else {
      setEditingExpense(null);
      setFormExpenseName('');
      setFormAmount('');
      setFormFrequency('monthly');
      setFormCategoryId('');
      setFormNotes('');
    }
    setShowExpenseDialog(true);
  };

  const handleCloseExpenseDialog = () => {
    setShowExpenseDialog(false);
    setEditingExpense(null);
    setFormExpenseName('');
    setFormAmount('');
    setFormFrequency('monthly');
    setFormCategoryId('');
    setFormNotes('');
  };

  const handleSubmitExpense = async () => {
    if (!formExpenseName || !formAmount || !formCategoryId) {
      toast.error('Please fill in all required fields');
      return;
    }

    const amount = Number.parseFloat(formAmount);
    if (Number.isNaN(amount) || amount <= 0) {
      toast.error('Amount must be greater than 0');
      return;
    }

    setSubmittingExpense(true);
    try {
      if (editingExpense) {
        await financialService.expenses.update(editingExpense.id, {
          expense_name: formExpenseName,
          amount,
          frequency: formFrequency,
          category_id: Number.parseInt(formCategoryId),
          notes: formNotes || undefined,
        });
        toast.success('Expense updated');
      } else {
        const data: ExpenseCreate = {
          expense_name: formExpenseName,
          amount,
          frequency: formFrequency,
          category_id: Number.parseInt(formCategoryId),
          notes: formNotes || undefined,
        };
        await financialService.expenses.create(data);
        toast.success('Expense created');
      }
      handleCloseExpenseDialog();
      fetchData();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSubmittingExpense(false);
    }
  };

  const handleDeleteExpense = async () => {
    if (!deleteExpense) return;

    try {
      await financialService.expenses.delete(deleteExpense.id);
      toast.success('Expense deleted');
      setDeleteExpense(null);
      fetchData();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  // Helper functions
  const getAccountName = (accountId: number) => {
    return accounts.find(a => a.id === accountId)?.account_name || 'Unknown';
  };

  const getCategoryName = (categoryId: number) => {
    return categories.find(c => c.id === categoryId)?.category_name || 'Unknown';
  };

  const getCategoryColor = (categoryId: number) => {
    return categories.find(c => c.id === categoryId)?.color || '#3B82F6';
  };

  const getExpenseCountForCategory = (categoryId: number) => {
    return expenses.filter(e => e.category_id === categoryId).length;
  };

  if (loading) {
    return <PageLoader message="Loading expenses..." />;
  }

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardDescription>Total Monthly Expenses</CardDescription>
          <CardTitle className="text-3xl">{formatCurrency(totalMonthlyExpenses)}</CardTitle>
        </CardHeader>
      </Card>

      {/* Split View: Categories and Expenses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* LEFT: Categories */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Expense Categories</CardTitle>
                <CardDescription>{categories.length} categories</CardDescription>
              </div>
              <Button onClick={() => handleOpenCategoryDialog()} size="sm">
                <Plus className="mr-2 h-4 w-4" />
                Add Category
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {categories.length === 0 ? (
              <EmptyState
                title="No categories yet"
                description="Create categories to organize your expenses."
                action={{
                  label: 'Add First Category',
                  onClick: () => handleOpenCategoryDialog(),
                }}
              />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Category</TableHead>
                    <TableHead>Account</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {categories.map((category) => (
                    <TableRow key={category.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div
                            className="w-3 h-3 rounded-full flex-shrink-0"
                            style={{ backgroundColor: category.color || '#3B82F6' }}
                          />
                          <span className="font-medium">{category.category_name}</span>
                          <Badge variant="secondary" className="text-xs">
                            {getExpenseCountForCategory(category.id)}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm text-gray-600">
                        {getAccountName(category.bank_account_id)}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleOpenCategoryDialog(category)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setDeleteCategory(category)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* RIGHT: Expenses */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Expenses</CardTitle>
                <CardDescription>{filteredExpenses.length} expenses</CardDescription>
              </div>
              <Button onClick={() => handleOpenExpenseDialog()} size="sm" disabled={categories.length === 0}>
                <Plus className="mr-2 h-4 w-4" />
                Add Expense
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Filter */}
            <div className="space-y-2">
              <Label>Filter by Category</Label>
              <Select value={selectedCategoryFilter} onValueChange={setSelectedCategoryFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id.toString()}>
                      {cat.category_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Expenses List */}
            {filteredExpenses.length === 0 ? (
              <EmptyState
                title={categories.length === 0 ? "Create a category first" : "No expenses yet"}
                description={
                  categories.length === 0
                    ? "You need to create at least one category before adding expenses."
                    : "Add your recurring expenses to calculate budget transfers."
                }
                action={categories.length > 0 ? {
                  label: 'Add First Expense',
                  onClick: () => handleOpenExpenseDialog(),
                } : undefined}
              />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Expense</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredExpenses.map((expense) => (
                    <TableRow key={expense.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div
                            className="w-2 h-2 rounded-full flex-shrink-0"
                            style={{ backgroundColor: getCategoryColor(expense.category_id) }}
                          />
                          <div>
                            <div className="font-medium">{expense.expense_name}</div>
                            <div className="text-xs text-gray-500">{getCategoryName(expense.category_id)}</div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div>{formatCurrency(expense.amount)}</div>
                          <Badge variant="secondary" className="text-xs">
                            {formatFrequency(expense.frequency)}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleOpenExpenseDialog(expense)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setDeleteExpense(expense)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Category Dialog */}
      <Dialog open={showCategoryDialog} onOpenChange={setShowCategoryDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingCategory ? 'Edit' : 'Add'} Expense Category</DialogTitle>
            <DialogDescription>
              Categories link expenses to specific bank accounts for budget calculations.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="categoryName">Category Name *</Label>
              <Input
                id="categoryName"
                value={formCategoryName}
                onChange={(e) => setFormCategoryName(e.target.value)}
                placeholder="Rent, Groceries, Insurance, etc."
                maxLength={255}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="bankAccount">Bank Account *</Label>
              <Select value={formBankAccountId} onValueChange={setFormBankAccountId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select an account" />
                </SelectTrigger>
                <SelectContent>
                  {accounts.map((account) => (
                    <SelectItem key={account.id} value={account.id.toString()}>
                      {account.account_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="color">Color</Label>
              <Input
                id="color"
                type="color"
                value={formColor}
                onChange={(e) => setFormColor(e.target.value)}
                className="w-20 h-10 cursor-pointer"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCloseCategoryDialog}>
              Cancel
            </Button>
            <LoadingButton onClick={handleSubmitCategory} loading={submittingCategory}>
              {editingCategory ? 'Update' : 'Create'}
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Expense Dialog */}
      <Dialog open={showExpenseDialog} onOpenChange={setShowExpenseDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingExpense ? 'Edit' : 'Add'} Expense</DialogTitle>
            <DialogDescription>
              Track recurring expenses for budget planning.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="expenseName">Expense Name *</Label>
              <Input
                id="expenseName"
                value={formExpenseName}
                onChange={(e) => setFormExpenseName(e.target.value)}
                placeholder="Monthly Rent, Weekly Groceries, etc."
                maxLength={255}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="amount">Amount *</Label>
                <Input
                  id="amount"
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={formAmount}
                  onChange={(e) => setFormAmount(e.target.value)}
                  placeholder="0.00"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="frequency">Frequency *</Label>
                <Select value={formFrequency} onValueChange={(value) => setFormFrequency(value as ExpenseFrequency)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="fortnightly">Fortnightly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                    <SelectItem value="bi_monthly">Bi-Monthly</SelectItem>
                    <SelectItem value="quarterly">Quarterly</SelectItem>
                    <SelectItem value="semi_annually">Semi-Annually</SelectItem>
                    <SelectItem value="yearly">Yearly</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Category *</Label>
              <Select value={formCategoryId} onValueChange={setFormCategoryId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id.toString()}>
                      {category.category_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea
                id="notes"
                value={formNotes}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setFormNotes(e.target.value)}
                placeholder="Optional notes"
                maxLength={1000}
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCloseExpenseDialog}>
              Cancel
            </Button>
            <LoadingButton onClick={handleSubmitExpense} loading={submittingExpense}>
              {editingExpense ? 'Update' : 'Create'}
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Category Confirmation */}
      {deleteCategory && (
        <ConfirmDialog
          open={!!deleteCategory}
          onOpenChange={(open) => !open && setDeleteCategory(null)}
          onConfirm={handleDeleteCategory}
          title="Delete Expense Category?"
          description={`Are you sure you want to delete "${deleteCategory.category_name}"? This will also delete all ${getExpenseCountForCategory(deleteCategory.id)} expense(s) in this category.`}
          confirmText="Delete"
          variant="destructive"
        />
      )}

      {/* Delete Expense Confirmation */}
      {deleteExpense && (
        <ConfirmDialog
          open={!!deleteExpense}
          onOpenChange={(open) => !open && setDeleteExpense(null)}
          onConfirm={handleDeleteExpense}
          title="Delete Expense?"
          description={`Are you sure you want to delete "${deleteExpense.expense_name}"?`}
          confirmText="Delete"
          variant="destructive"
        />
      )}
    </div>
  );
}
