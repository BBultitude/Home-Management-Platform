import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/common/EmptyState';
import { PageLoader } from '@/components/common/PageLoader';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { LoadingButton } from '@/components/ui/loading-button';
import { financialService } from '@/services/financialService';
import type { IncomeSource, IncomeSourceCreate, IncomeFrequency } from '@/services/financialService';
import { getErrorMessage } from '@/lib/errorMessages';
import { toast } from 'sonner';
import { normalizeToMonthly, formatCurrency, formatFrequency } from '@/lib/frequencyUtils';

export function IncomeTab() {
  const [sources, setSources] = useState<IncomeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingSource, setEditingSource] = useState<IncomeSource | null>(null);
  const [deleteSource, setDeleteSource] = useState<IncomeSource | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [formName, setFormName] = useState('');
  const [formAmount, setFormAmount] = useState('');
  const [formFrequency, setFormFrequency] = useState<IncomeFrequency>('monthly');

  // Summary stats
  const totalMonthlyIncome = sources.reduce((sum, s) => sum + normalizeToMonthly(s.amount, s.frequency), 0);

  // Fetch sources
  const fetchSources = async () => {
    setLoading(true);
    try {
      const response = await financialService.income.list();
      setSources(response.income_sources);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSources();
  }, []);

  const handleOpenDialog = (source?: IncomeSource) => {
    if (source) {
      setEditingSource(source);
      setFormName(source.source_name);
      setFormAmount(source.amount.toString());
      setFormFrequency(source.frequency);
    } else {
      setEditingSource(null);
      setFormName('');
      setFormAmount('');
      setFormFrequency('monthly');
    }
    setShowDialog(true);
  };

  const handleCloseDialog = () => {
    setShowDialog(false);
    setEditingSource(null);
    setFormName('');
    setFormAmount('');
    setFormFrequency('monthly');
  };

  const handleSubmit = async () => {
    if (!formName || !formAmount) {
      toast.error('Please fill in all required fields');
      return;
    }

    const amount = parseFloat(formAmount);
    if (isNaN(amount) || amount <= 0) {
      toast.error('Amount must be greater than 0');
      return;
    }

    setSubmitting(true);
    try {
      if (editingSource) {
        // Update existing
        await financialService.income.update(editingSource.id, {
          source_name: formName,
          amount,
          frequency: formFrequency,
        });
        toast.success('Income source updated');
      } else {
        // Create new
        const data: IncomeSourceCreate = {
          source_name: formName,
          amount,
          frequency: formFrequency,
        };
        await financialService.income.create(data);
        toast.success('Income source created');
      }
      handleCloseDialog();
      fetchSources();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteSource) return;

    try {
      await financialService.income.delete(deleteSource.id);
      toast.success('Income source deleted');
      setDeleteSource(null);
      fetchSources();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  if (loading) {
    return <PageLoader message="Loading income sources..." />;
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Income Sources</CardDescription>
            <CardTitle className="text-3xl">{sources.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Monthly Income</CardDescription>
            <CardTitle className="text-3xl">{formatCurrency(totalMonthlyIncome)}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Sources Table */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Income Sources</CardTitle>
              <CardDescription>Manage your income streams</CardDescription>
            </div>
            <Button onClick={() => handleOpenDialog()}>
              <Plus className="mr-2 h-4 w-4" />
              Add Source
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {sources.length === 0 ? (
            <EmptyState
              title="No income sources yet"
              description="Add your income sources to start building your budget."
              action={{
                label: 'Add First Source',
                onClick: () => handleOpenDialog(),
              }}
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Source Name</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Frequency</TableHead>
                  <TableHead>Monthly Equivalent</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sources.map((source) => (
                  <TableRow key={source.id}>
                    <TableCell className="font-medium">{source.source_name}</TableCell>
                    <TableCell>{formatCurrency(source.amount)}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{formatFrequency(source.frequency)}</Badge>
                    </TableCell>
                    <TableCell>{formatCurrency(normalizeToMonthly(source.amount, source.frequency))}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleOpenDialog(source)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setDeleteSource(source)}
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

      {/* Create/Edit Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingSource ? 'Edit' : 'Add'} Income Source</DialogTitle>
            <DialogDescription>
              {editingSource ? 'Update' : 'Add'} an income source for budget planning.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Source Name *</Label>
              <Input
                id="name"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="Salary, Rental Income, etc."
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
                <Select value={formFrequency} onValueChange={(value) => setFormFrequency(value as IncomeFrequency)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="fortnightly">Fortnightly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                    <SelectItem value="yearly">Yearly</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCloseDialog}>
              Cancel
            </Button>
            <LoadingButton onClick={handleSubmit} loading={submitting}>
              {editingSource ? 'Update' : 'Create'}
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      {deleteSource && (
        <ConfirmDialog
          open={!!deleteSource}
          onOpenChange={(open) => !open && setDeleteSource(null)}
          onConfirm={handleDelete}
          title="Delete Income Source?"
          description={`Are you sure you want to delete "${deleteSource.source_name}"? This will affect budget calculations.`}
          confirmText="Delete"
          variant="destructive"
        />
      )}
    </div>
  );
}
