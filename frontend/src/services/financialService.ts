import { apiClient } from '@/lib/api';

// ============================================================================
// INCOME SOURCES
// ============================================================================

export type IncomeFrequency = 'daily' | 'weekly' | 'fortnightly' | 'monthly' | 'yearly';

export interface IncomeSource {
  id: number;
  source_name: string;
  amount: number;
  frequency: IncomeFrequency;
  created_at: string;
  updated_at: string;
}

export interface IncomeSourceCreate {
  source_name: string;
  amount: number;
  frequency: IncomeFrequency;
}

export interface IncomeSourceUpdate {
  source_name?: string;
  amount?: number;
  frequency?: IncomeFrequency;
}

export interface IncomeSourceListResponse {
  income_sources: IncomeSource[];
  total: number;
}

// ============================================================================
// BANK ACCOUNTS
// ============================================================================

export type AccountType = 'checking' | 'savings' | 'offset';

export interface BankAccount {
  id: number;
  account_name: string;
  account_type: AccountType;
  current_balance: number | null;
  created_at: string;
  updated_at: string;
}

export interface BankAccountCreate {
  account_name: string;
  account_type: AccountType;
  current_balance?: number;
}

export interface BankAccountUpdate {
  account_name?: string;
  account_type?: AccountType;
  current_balance?: number;
}

export interface BankAccountListResponse {
  accounts: BankAccount[];
  total: number;
}

// ============================================================================
// EXPENSE CATEGORIES
// ============================================================================

export interface ExpenseCategory {
  id: number;
  category_name: string;
  bank_account_id: number;
  color: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExpenseCategoryCreate {
  category_name: string;
  bank_account_id: number;
  color?: string;
}

export interface ExpenseCategoryUpdate {
  category_name?: string;
  bank_account_id?: number;
  color?: string;
}

export interface ExpenseCategoryListResponse {
  categories: ExpenseCategory[];
  total: number;
}

// ============================================================================
// EXPENSES
// ============================================================================

export type ExpenseFrequency = 'daily' | 'weekly' | 'fortnightly' | 'monthly' | 'yearly';

export interface Expense {
  id: number;
  expense_name: string;
  amount: number;
  frequency: ExpenseFrequency;
  category_id: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExpenseCreate {
  expense_name: string;
  amount: number;
  frequency: ExpenseFrequency;
  category_id: number;
  notes?: string;
}

export interface ExpenseUpdate {
  expense_name?: string;
  amount?: number;
  frequency?: ExpenseFrequency;
  category_id?: number;
  notes?: string;
}

export interface ExpenseListResponse {
  expenses: Expense[];
  total: number;
}

// ============================================================================
// UTILITIES
// ============================================================================

export type UtilityType = 'electricity' | 'gas' | 'water' | 'internet' | 'mobile' | 'rates';

export interface Utility {
  id: number;
  utility_type: UtilityType;
  provider: string;
  billing_period_start: string;
  billing_period_end: string;
  usage: number;
  unit: string;
  cost: number;
  cost_per_unit: number;
  attachment_id: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface UtilityCreate {
  utility_type: UtilityType;
  provider: string;
  billing_period_start: string;
  billing_period_end: string;
  usage: number;
  unit: string;
  cost: number;
  attachment_id?: number;
  notes?: string;
}

export interface UtilityUpdate {
  utility_type?: UtilityType;
  provider?: string;
  billing_period_start?: string;
  billing_period_end?: string;
  usage?: number;
  unit?: string;
  cost?: number;
  attachment_id?: number;
  notes?: string;
}

export interface UtilityListResponse {
  utilities: Utility[];
  total: number;
}

export interface UtilityStatsResponse {
  utility_type: UtilityType;
  entry_count: number;
  total_cost: number;
  total_usage: number;
  average_cost: number;
  period_start: string | null;
  period_end: string | null;
}

// ============================================================================
// BUDGET
// ============================================================================

export interface BudgetCalculationRequest {
  pay_frequency: IncomeFrequency;
}

export interface BudgetTransfer {
  account_id: number;
  account_name: string;
  amount: number;
  expenses: string[];
}

export interface BudgetCalculationResponse {
  pay_frequency: IncomeFrequency;
  total_income: number;
  total_expenses: number;
  surplus: number;
  transfers: BudgetTransfer[];
}

export interface BudgetSummaryResponse {
  total_monthly_income: number;
  total_monthly_expenses: number;
  monthly_surplus: number;
  account_allocations: Record<string, number>;
}

// ============================================================================
// API SERVICE
// ============================================================================

export const financialService = {
  // Income Sources
  income: {
    list: async (params?: { limit?: number; offset?: number }): Promise<IncomeSourceListResponse> => {
      return await apiClient.get('/financial/income', { params }) as IncomeSourceListResponse;
    },

    get: async (id: number): Promise<IncomeSource> => {
      return await apiClient.get(`/financial/income/${id}`) as IncomeSource;
    },

    create: async (data: IncomeSourceCreate): Promise<IncomeSource> => {
      return await apiClient.post('/financial/income', data) as IncomeSource;
    },

    update: async (id: number, data: IncomeSourceUpdate): Promise<IncomeSource> => {
      return await apiClient.put(`/financial/income/${id}`, data) as IncomeSource;
    },

    delete: async (id: number): Promise<{ message: string; id: number }> => {
      return await apiClient.delete(`/financial/income/${id}`) as { message: string; id: number };
    },
  },

  // Bank Accounts
  accounts: {
    list: async (params?: { limit?: number; offset?: number }): Promise<BankAccountListResponse> => {
      return await apiClient.get('/financial/bank-accounts', { params }) as BankAccountListResponse;
    },

    get: async (id: number): Promise<BankAccount> => {
      return await apiClient.get(`/financial/bank-accounts/${id}`) as BankAccount;
    },

    create: async (data: BankAccountCreate): Promise<BankAccount> => {
      return await apiClient.post('/financial/bank-accounts', data) as BankAccount;
    },

    update: async (id: number, data: BankAccountUpdate): Promise<BankAccount> => {
      return await apiClient.put(`/financial/bank-accounts/${id}`, data) as BankAccount;
    },

    delete: async (id: number): Promise<{ message: string; id: number }> => {
      return await apiClient.delete(`/financial/bank-accounts/${id}`) as { message: string; id: number };
    },
  },

  // Expense Categories
  categories: {
    list: async (params?: { bank_account_id?: number; limit?: number; offset?: number }): Promise<ExpenseCategoryListResponse> => {
      return await apiClient.get('/financial/expense-categories', { params }) as ExpenseCategoryListResponse;
    },

    get: async (id: number): Promise<ExpenseCategory> => {
      return await apiClient.get(`/financial/expense-categories/${id}`) as ExpenseCategory;
    },

    create: async (data: ExpenseCategoryCreate): Promise<ExpenseCategory> => {
      return await apiClient.post('/financial/expense-categories', data) as ExpenseCategory;
    },

    update: async (id: number, data: ExpenseCategoryUpdate): Promise<ExpenseCategory> => {
      return await apiClient.put(`/financial/expense-categories/${id}`, data) as ExpenseCategory;
    },

    delete: async (id: number): Promise<{ message: string; id: number }> => {
      return await apiClient.delete(`/financial/expense-categories/${id}`) as { message: string; id: number };
    },
  },

  // Expenses
  expenses: {
    list: async (params?: { category_id?: number; limit?: number; offset?: number }): Promise<ExpenseListResponse> => {
      return await apiClient.get('/financial/expenses', { params }) as ExpenseListResponse;
    },

    get: async (id: number): Promise<Expense> => {
      return await apiClient.get(`/financial/expenses/${id}`) as Expense;
    },

    create: async (data: ExpenseCreate): Promise<Expense> => {
      return await apiClient.post('/financial/expenses', data) as Expense;
    },

    update: async (id: number, data: ExpenseUpdate): Promise<Expense> => {
      return await apiClient.put(`/financial/expenses/${id}`, data) as Expense;
    },

    delete: async (id: number): Promise<{ message: string; id: number }> => {
      return await apiClient.delete(`/financial/expenses/${id}`) as { message: string; id: number };
    },
  },

  // Utilities
  utilities: {
    list: async (params?: {
      utility_type?: UtilityType;
      start_date?: string;
      end_date?: string;
      limit?: number;
      offset?: number;
    }): Promise<UtilityListResponse> => {
      return await apiClient.get('/financial/utilities', { params }) as UtilityListResponse;
    },

    get: async (id: number): Promise<Utility> => {
      return await apiClient.get(`/financial/utilities/${id}`) as Utility;
    },

    create: async (data: UtilityCreate): Promise<Utility> => {
      return await apiClient.post('/financial/utilities', data) as Utility;
    },

    update: async (id: number, data: UtilityUpdate): Promise<Utility> => {
      return await apiClient.put(`/financial/utilities/${id}`, data) as Utility;
    },

    delete: async (id: number): Promise<{ message: string; id: number }> => {
      return await apiClient.delete(`/financial/utilities/${id}`) as { message: string; id: number };
    },

    stats: async (
      utilityType: UtilityType,
      params?: { start_date?: string; end_date?: string }
    ): Promise<UtilityStatsResponse> => {
      return await apiClient.get(`/financial/utilities/stats/${utilityType}`, { params }) as UtilityStatsResponse;
    },
  },

  // Budget Calculator
  budget: {
    calculate: async (data: BudgetCalculationRequest): Promise<BudgetCalculationResponse> => {
      return await apiClient.post('/financial/budget/calculate', data) as BudgetCalculationResponse;
    },

    summary: async (): Promise<BudgetSummaryResponse> => {
      return await apiClient.get('/financial/budget/summary') as BudgetSummaryResponse;
    },
  },
};
