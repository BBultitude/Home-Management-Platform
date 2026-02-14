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
import type { BankAccount, BankAccountCreate, AccountType } from '@/services/financialService';
import { getErrorMessage } from '@/lib/errorMessages';
import { toast } from 'sonner';

export function AccountsTab() {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingAccount, setEditingAccount] = useState<BankAccount | null>(null);
  const [deleteAccount, setDeleteAccount] = useState<BankAccount | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [formName, setFormName] = useState('');
  const [formType, setFormType] = useState<AccountType>('checking');

  // Fetch accounts
  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const response = await financialService.accounts.list();
      setAccounts(response.accounts);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const handleOpenDialog = (account?: BankAccount) => {
    if (account) {
      setEditingAccount(account);
      setFormName(account.account_name);
      setFormType(account.account_type);
    } else {
      setEditingAccount(null);
      setFormName('');
      setFormType('checking');
    }
    setShowDialog(true);
  };

  const handleCloseDialog = () => {
    setShowDialog(false);
    setEditingAccount(null);
    setFormName('');
    setFormType('checking');
  };

  const handleSubmit = async () => {
    if (!formName) {
      toast.error('Please enter an account name');
      return;
    }

    setSubmitting(true);
    try {
      if (editingAccount) {
        // Update existing
        await financialService.accounts.update(editingAccount.id, {
          account_name: formName,
          account_type: formType,
        });
        toast.success('Bank account updated');
      } else {
        // Create new
        const data: BankAccountCreate = {
          account_name: formName,
          account_type: formType,
        };
        await financialService.accounts.create(data);
        toast.success('Bank account created');
      }
      handleCloseDialog();
      fetchAccounts();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteAccount) return;

    try {
      await financialService.accounts.delete(deleteAccount.id);
      toast.success('Bank account deleted');
      setDeleteAccount(null);
      fetchAccounts();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const getAccountTypeBadge = (type: AccountType) => {
    const colors = {
      checking: 'bg-blue-100 text-blue-800',
      savings: 'bg-green-100 text-green-800',
      offset: 'bg-purple-100 text-purple-800',
    };
    return (
      <Badge className={colors[type]} variant="secondary">
        {type.charAt(0).toUpperCase() + type.slice(1)}
      </Badge>
    );
  };

  if (loading) {
    return <PageLoader message="Loading bank accounts..." />;
  }

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardDescription>Total Accounts</CardDescription>
          <CardTitle className="text-3xl">{accounts.length}</CardTitle>
        </CardHeader>
      </Card>

      {/* Accounts Table */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Bank Accounts</CardTitle>
              <CardDescription>Manage your bank accounts for budget allocation</CardDescription>
            </div>
            <Button onClick={() => handleOpenDialog()}>
              <Plus className="mr-2 h-4 w-4" />
              Add Account
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {accounts.length === 0 ? (
            <EmptyState
              title="No bank accounts yet"
              description="Add your bank accounts to track balances and allocate expenses."
              action={{
                label: 'Add First Account',
                onClick: () => handleOpenDialog(),
              }}
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Account Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {accounts.map((account) => (
                  <TableRow key={account.id}>
                    <TableCell className="font-medium">{account.account_name}</TableCell>
                    <TableCell>{getAccountTypeBadge(account.account_type)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleOpenDialog(account)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setDeleteAccount(account)}
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
            <DialogTitle>{editingAccount ? 'Edit' : 'Add'} Bank Account</DialogTitle>
            <DialogDescription>
              {editingAccount ? 'Update' : 'Add'} a bank account for expense allocation.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Account Name *</Label>
              <Input
                id="name"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="Everyday, Bills, Savings, etc."
                maxLength={255}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="type">Account Type *</Label>
              <Select value={formType} onValueChange={(value) => setFormType(value as AccountType)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="checking">Checking</SelectItem>
                  <SelectItem value="savings">Savings</SelectItem>
                  <SelectItem value="offset">Offset</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCloseDialog}>
              Cancel
            </Button>
            <LoadingButton onClick={handleSubmit} loading={submitting}>
              {editingAccount ? 'Update' : 'Create'}
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      {deleteAccount && (
        <ConfirmDialog
          open={!!deleteAccount}
          onOpenChange={(open) => !open && setDeleteAccount(null)}
          onConfirm={handleDelete}
          title="Delete Bank Account?"
          description={`Are you sure you want to delete "${deleteAccount.account_name}"? This will also delete all associated expense categories and their expenses.`}
          confirmText="Delete"
          variant="destructive"
        />
      )}
    </div>
  );
}
