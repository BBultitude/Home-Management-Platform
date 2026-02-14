import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { IncomeTab } from './IncomeTab';
import { AccountsTab } from './AccountsTab';
import { ExpensesTab } from './ExpensesTab';
import { UtilitiesTab } from './UtilitiesTab';
import { BudgetTab } from './BudgetTab';

export default function FinancialManagement() {
  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Financial Management</h1>
        <p className="text-gray-600 mt-1">
          Manage income, expenses, bank accounts, and budget planning
        </p>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="income" className="space-y-6">
        <TabsList>
          <TabsTrigger value="income">Income</TabsTrigger>
          <TabsTrigger value="accounts">Accounts</TabsTrigger>
          <TabsTrigger value="expenses">Expenses</TabsTrigger>
          <TabsTrigger value="utilities">Utilities</TabsTrigger>
          <TabsTrigger value="budget">Budget</TabsTrigger>
        </TabsList>

        <TabsContent value="income">
          <IncomeTab />
        </TabsContent>

        <TabsContent value="accounts">
          <AccountsTab />
        </TabsContent>

        <TabsContent value="expenses">
          <ExpensesTab />
        </TabsContent>

        <TabsContent value="utilities">
          <UtilitiesTab />
        </TabsContent>

        <TabsContent value="budget">
          <BudgetTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
