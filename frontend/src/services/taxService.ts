import { apiClient } from '@/lib/api';

// Types based on backend schemas
export interface WFHEntry {
  id: number;
  user_id: number;
  date: string; // ISO date string
  hours: number;
  notes?: string;
  deduction_amount: number;
  created_at: string;
  updated_at: string;
}

export interface WFHEntryCreate {
  date: string; // ISO date string
  hours: number;
  notes?: string;
}

export interface WFHEntryUpdate {
  hours?: number;
  notes?: string;
}

export interface WFHListResponse {
  entries: WFHEntry[];
  total: number;
  start_date?: string;
  end_date?: string;
}

export interface WFHSummary {
  financial_year: number;
  fy_start_date: string;
  fy_end_date: string;
  total_days: number;
  total_hours: number;
  ato_rate_per_hour: number;
  total_deduction: number;
  entries: Array<{
    date: string;
    hours: number;
    deduction: number;
  }>;
}

export interface TravelEntry {
  id: number;
  user_id: number;
  date: string;
  purpose: string;
  start_location: string;
  end_location: string;
  distance_km: number;
  deduction_amount?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface TravelEntryCreate {
  date: string;
  purpose: string;
  start_location: string;
  end_location: string;
  distance_km: number;
  notes?: string;
}

export interface TravelEntryUpdate {
  purpose?: string;
  start_location?: string;
  end_location?: string;
  distance_km?: number;
  notes?: string;
}

export interface TravelListResponse {
  entries: TravelEntry[];
  total: number;
  start_date?: string;
  end_date?: string;
}

export interface TravelSummary {
  financial_year: number;
  fy_start_date: string;
  fy_end_date: string;
  total_trips: number;
  total_km: number;
  rate_per_km: number;
  total_deduction: number;
  entries: Array<{
    date: string;
    start_location: string;
    end_location: string;
    distance_km: number;
    deduction: number;
  }>;
}

// WFH API calls
export const taxService = {
  // Work From Home
  wfh: {
    list: async (params?: { start_date?: string; end_date?: string; limit?: number; offset?: number }): Promise<WFHListResponse> => {
      return await apiClient.get('/tax/wfh', { params }) as WFHListResponse;
    },

    get: async (id: number): Promise<WFHEntry> => {
      return await apiClient.get(`/tax/wfh/${id}`) as WFHEntry;
    },

    create: async (data: WFHEntryCreate): Promise<WFHEntry> => {
      return await apiClient.post('/tax/wfh', data) as WFHEntry;
    },

    update: async (id: number, data: WFHEntryUpdate): Promise<WFHEntry> => {
      return await apiClient.put(`/tax/wfh/${id}`, data) as WFHEntry;
    },

    delete: async (id: number): Promise<{ message: string; entry_id: number }> => {
      return await apiClient.delete(`/tax/wfh/${id}`) as { message: string; entry_id: number };
    },

    summary: async (financialYear: string, ratePerHour?: number): Promise<WFHSummary> => {
      // financialYear format: "2024-2025" - backend expects END year (2025)
      const [, endYear] = financialYear.split('-').map(Number);
      const params = ratePerHour !== undefined ? { rate_per_hour: ratePerHour } : {};
      return await apiClient.get(`/tax/wfh/summary/fy/${endYear}`, { params }) as WFHSummary;
    },

    export: async (financialYear: string, ratePerHour?: number): Promise<Blob> => {
      // financialYear format: "2024-2025" - backend expects END year (2025)
      const [, endYear] = financialYear.split('-').map(Number);
      const params = ratePerHour !== undefined ? { rate_per_hour: ratePerHour } : {};
      return await apiClient.get(`/tax/wfh/export/fy/${endYear}/csv`, {
        params,
        responseType: 'blob'
      }) as Blob;
    },
  },

  // Work Travel
  travel: {
    list: async (params?: { start_date?: string; end_date?: string; limit?: number; offset?: number }): Promise<TravelListResponse> => {
      return await apiClient.get('/tax/travel', { params }) as TravelListResponse;
    },

    get: async (id: number): Promise<TravelEntry> => {
      return await apiClient.get(`/tax/travel/${id}`) as TravelEntry;
    },

    create: async (data: TravelEntryCreate): Promise<TravelEntry> => {
      return await apiClient.post('/tax/travel', data) as TravelEntry;
    },

    update: async (id: number, data: TravelEntryUpdate): Promise<TravelEntry> => {
      return await apiClient.put(`/tax/travel/${id}`, data) as TravelEntry;
    },

    delete: async (id: number): Promise<{ message: string; entry_id: number }> => {
      return await apiClient.delete(`/tax/travel/${id}`) as { message: string; entry_id: number };
    },

    summary: async (financialYear: string, ratePerKm?: number): Promise<TravelSummary> => {
      // financialYear format: "2024-2025" - backend expects END year (2025)
      const [, endYear] = financialYear.split('-').map(Number);
      const params = ratePerKm !== undefined ? { rate_per_km: ratePerKm } : {};
      return await apiClient.get(`/tax/travel/summary/fy/${endYear}`, { params }) as TravelSummary;
    },

    export: async (financialYear: string, ratePerKm?: number): Promise<Blob> => {
      // financialYear format: "2024-2025" - backend expects END year (2025)
      const [, endYear] = financialYear.split('-').map(Number);
      const params = ratePerKm !== undefined ? { rate_per_km: ratePerKm } : {};
      return await apiClient.get(`/tax/travel/export/fy/${endYear}/csv`, {
        params,
        responseType: 'blob'
      }) as Blob;
    },
  },
};
