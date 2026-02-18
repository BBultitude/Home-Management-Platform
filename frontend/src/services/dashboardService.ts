import { apiClient } from '@/lib/api';

export interface AlertsWidget {
  insurance_renewals: {
    urgent: number;   // within 7 days
    upcoming: number; // 7-30 days
  };
  document_expiries: {
    urgent: number;
    upcoming: number;
  };
  quote_expiries: number;
  total_alerts: number;
}

export interface PriorityItem {
  id: string;
  name: string;
  net_score: number;
  benefit_score: number;
  cost_score: number;
  estimated_cost: number;
}

export interface PrioritiesWidget {
  top_priorities: PriorityItem[];
  total_priorities: number;
}

export const dashboardService = {
  alerts: async (): Promise<AlertsWidget> => {
    return await apiClient.get('/dashboard/alerts') as AlertsWidget;
  },

  priorities: async (limit = 5): Promise<PrioritiesWidget> => {
    return await apiClient.get('/dashboard/priorities', { params: { limit } }) as PrioritiesWidget;
  },
};
