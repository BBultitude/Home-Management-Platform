import { useState } from 'react';
import { Calculator, AlertCircle, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { LoadingButton } from '@/components/ui/loading-button';
import { financialService } from '@/services/financialService';
import type { BudgetCalculationResponse, IncomeFrequency } from '@/services/financialService';
import { getErrorMessage } from '@/lib/errorMessages';
import { toast } from 'sonner';
import { formatCurrency, formatFrequency } from '@/lib/frequencyUtils';
import { cn } from '@/lib/utils';

export function BudgetTab() {
  const [payFrequency, setPayFrequency] = useState<IncomeFrequency>('monthly');
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState<BudgetCalculationResponse | null>(null);
  const [expandedTransfers, setExpandedTransfers] = useState<Set<number>>(new Set());

  const handleCalculate = async () => {
    setCalculating(true);
    try {
      const response = await financialService.budget.calculate({ pay_frequency: payFrequency });
      setResult(response);
      if (response.transfers.length === 0) {
        toast.info('No expenses configured. Add expenses to see transfer amounts.');
      } else {
        toast.success('Budget calculated successfully');
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      setResult(null);
    } finally {
      setCalculating(false);
    }
  };

  const toggleTransferExpanded = (accountId: number) => {
    const newExpanded = new Set(expandedTransfers);
    if (newExpanded.has(accountId)) {
      newExpanded.delete(accountId);
    } else {
      newExpanded.add(accountId);
    }
    setExpandedTransfers(newExpanded);
  };

  const frequencies: IncomeFrequency[] = ['daily', 'weekly', 'fortnightly', 'monthly', 'yearly'];

  return (
    <div className="space-y-6">
      {/* Frequency Selector */}
      <Card>
        <CardHeader>
          <CardTitle>Budget Calculator</CardTitle>
          <CardDescription>
            Calculate how much to transfer to each account based on your pay frequency
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Pay Frequency</Label>
            <div className="flex flex-wrap gap-2">
              {frequencies.map((freq) => (
                <button
                  key={freq}
                  onClick={() => setPayFrequency(freq)}
                  className={cn(
                    'px-4 py-2 rounded-md text-sm font-medium transition-colors',
                    payFrequency === freq
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  {formatFrequency(freq)}
                </button>
              ))}
            </div>
          </div>

          <LoadingButton onClick={handleCalculate} loading={calculating} className="w-full">
            <Calculator className="mr-2 h-4 w-4" />
            Calculate Budget
          </LoadingButton>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Total Income ({formatFrequency(result.pay_frequency)})</CardDescription>
                <CardTitle className="text-3xl">{formatCurrency(result.total_income)}</CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Total Expenses ({formatFrequency(result.pay_frequency)})</CardDescription>
                <CardTitle className="text-3xl">{formatCurrency(result.total_expenses)}</CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>
                  {result.surplus >= 0 ? 'Surplus' : 'Deficit'} ({formatFrequency(result.pay_frequency)})
                </CardDescription>
                <CardTitle className={cn(
                  "text-3xl",
                  result.surplus >= 0 ? "text-green-600" : "text-red-600"
                )}>
                  {formatCurrency(Math.abs(result.surplus))}
                </CardTitle>
              </CardHeader>
            </Card>
          </div>

          {/* Surplus/Deficit Alert */}
          {result.surplus >= 0 ? (
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                You have a surplus of {formatCurrency(result.surplus)} per {result.pay_frequency.toLowerCase()} period.
                Consider allocating this to savings or investments.
              </AlertDescription>
            </Alert>
          ) : (
            <Alert className="bg-red-50 border-red-200">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                You have a deficit of {formatCurrency(Math.abs(result.surplus))} per {result.pay_frequency.toLowerCase()} period.
                Review your expenses or increase income to balance your budget.
              </AlertDescription>
            </Alert>
          )}

          {/* Transfer Instructions */}
          <Card>
            <CardHeader>
              <CardTitle>Transfer Instructions</CardTitle>
              <CardDescription>
                Transfer these amounts to each account every {result.pay_frequency.toLowerCase()} period
              </CardDescription>
            </CardHeader>
            <CardContent>
              {result.transfers.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    No expenses configured. Add income sources, bank accounts, expense categories, and expenses to generate transfer instructions.
                  </AlertDescription>
                </Alert>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Account Name</TableHead>
                      <TableHead>Transfer Amount</TableHead>
                      <TableHead># of Expenses</TableHead>
                      <TableHead className="text-right">Details</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {result.transfers.map((transfer) => (
                      <>
                        <TableRow key={transfer.account_id} className="cursor-pointer hover:bg-gray-50">
                          <TableCell className="font-medium">{transfer.account_name}</TableCell>
                          <TableCell className="text-lg font-semibold text-primary">
                            {formatCurrency(transfer.amount)}
                          </TableCell>
                          <TableCell>
                            <span className="text-sm text-gray-600">{transfer.expenses.length} expenses</span>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleTransferExpanded(transfer.account_id)}
                            >
                              {expandedTransfers.has(transfer.account_id) ? (
                                <>
                                  Hide <ChevronUp className="ml-1 h-4 w-4" />
                                </>
                              ) : (
                                <>
                                  Show <ChevronDown className="ml-1 h-4 w-4" />
                                </>
                              )}
                            </Button>
                          </TableCell>
                        </TableRow>
                        {expandedTransfers.has(transfer.account_id) && (
                          <TableRow key={`${transfer.account_id}-details`}>
                            <TableCell colSpan={4} className="bg-gray-50">
                              <div className="py-3 px-4">
                                <p className="text-sm font-medium text-gray-700 mb-2">Expenses included:</p>
                                <ul className="list-disc list-inside space-y-1">
                                  {transfer.expenses.map((expense) => (
                                    <li key={expense} className="text-sm text-gray-600">{expense}</li>
                                  ))}
                                </ul>
                              </div>
                            </TableCell>
                          </TableRow>
                        )}
                      </>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Summary Info */}
          {result.transfers.length > 0 && (
            <Card className="bg-blue-50 border-blue-200">
              <CardHeader>
                <CardTitle className="text-blue-900">How to Use This Budget</CardTitle>
              </CardHeader>
              <CardContent className="text-blue-800 space-y-2">
                <p>
                  <strong>1.</strong> Every {result.pay_frequency.toLowerCase()} when you receive your income of{' '}
                  {formatCurrency(result.total_income)}, make these transfers:
                </p>
                <ul className="list-disc list-inside ml-4 space-y-1">
                  {result.transfers.map((transfer) => (
                    <li key={transfer.account_id}>
                      Transfer {formatCurrency(transfer.amount)} to {transfer.account_name}
                    </li>
                  ))}
                </ul>
                <p>
                  <strong>2.</strong> Total transfers: {formatCurrency(result.total_expenses)}
                </p>
                {result.surplus > 0 && (
                  <p>
                    <strong>3.</strong> You'll have {formatCurrency(result.surplus)} remaining for savings or discretionary spending
                  </p>
                )}
                <p className="text-sm mt-3">
                  <strong>Note:</strong> This calculation is based on your current income sources and expenses. Update them as needed to keep your budget accurate.
                </p>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* Help Text (shown when no calculation yet) */}
      {!result && (
        <Card className="bg-gray-50">
          <CardHeader>
            <CardTitle>Get Started</CardTitle>
          </CardHeader>
          <CardContent className="text-gray-600 space-y-3">
            <p>To use the budget calculator:</p>
            <ol className="list-decimal list-inside space-y-2 ml-2">
              <li>Add your income sources in the <strong>Income</strong> tab</li>
              <li>Create bank accounts in the <strong>Accounts</strong> tab</li>
              <li>Create expense categories and link them to accounts in the <strong>Expenses</strong> tab</li>
              <li>Add your recurring expenses in the <strong>Expenses</strong> tab</li>
              <li>Select your pay frequency above and click <strong>Calculate Budget</strong></li>
            </ol>
            <p className="mt-4">
              The calculator will normalize all your income and expenses to your pay frequency and show you exactly how much to transfer to each account.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
