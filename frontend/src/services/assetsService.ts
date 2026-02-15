/**
 * Assets & Documents Service
 * API client for insurance policies and document management
 */

import { apiClient } from '@/lib/api';

// ============================================================================
// INSURANCE POLICIES
// ============================================================================

export type PolicyType =
  | 'Home'
  | 'Car'
  | 'Health'
  | 'Life'
  | 'Pet'
  | 'Travel'
  | 'Contents'
  | 'Landlord'
  | 'Income Protection'
  | 'Other';

export type PremiumFrequency = 'Monthly' | 'Annually';

export interface InsurancePolicy {
  id: string; // UUID
  policy_type: PolicyType;
  provider: string;
  policy_number: string | null;
  coverage_amount: number | null;
  premium: number;
  premium_frequency: PremiumFrequency;
  excess: number | null;
  renewal_date: string; // ISO date
  coverage_notes: string | null;
  document_id: string | null;
  vehicle_id: string | null;
  days_until_renewal: number;
  created_at: string;
  updated_at: string;
}

export interface InsurancePolicyCreate {
  policy_type: PolicyType;
  provider: string;
  policy_number?: string;
  coverage_amount?: number;
  premium: number;
  premium_frequency: PremiumFrequency;
  excess?: number;
  renewal_date: string; // YYYY-MM-DD
  coverage_notes?: string;
  document_id?: number;
  vehicle_id?: string;
}

export interface InsurancePolicyUpdate {
  policy_type?: PolicyType;
  provider?: string;
  policy_number?: string;
  coverage_amount?: number;
  premium?: number;
  premium_frequency?: PremiumFrequency;
  excess?: number;
  renewal_date?: string;
  coverage_notes?: string;
  document_id?: number;
  vehicle_id?: string;
}

export interface InsurancePolicyListResponse {
  policies: InsurancePolicy[];
  total: number;
}

export interface RenewalAlert {
  policy_id: string;
  policy_type: PolicyType;
  provider: string;
  renewal_date: string;
  days_until_renewal: number;
  premium: number;
  premium_frequency: PremiumFrequency;
}

export interface RenewalAlertResponse {
  alerts_30_days: RenewalAlert[];
  alerts_7_days: RenewalAlert[];
}

// ============================================================================
// DOCUMENTS
// ============================================================================

export type DocumentType =
  | 'Contract'
  | 'Receipt'
  | 'Warranty'
  | 'Manual'
  | 'Certificate'
  | 'Legal'
  | 'Medical'
  | 'Financial'
  | 'Other';

export interface Document {
  id: string; // UUID
  document_type: DocumentType;
  title: string;
  description: string | null;
  category: string | null;
  tags: string[];
  uploaded_date: string; // ISO date
  expiry_date: string | null; // ISO date
  file_id: string;
  created_at: string;
}

export interface DocumentCreate {
  document_type: DocumentType;
  title: string;
  description?: string;
  category?: string;
  tags?: string[];
  uploaded_date?: string; // YYYY-MM-DD, defaults to today
  expiry_date?: string; // YYYY-MM-DD
  file_id: number;
}

export interface DocumentUpdate {
  document_type?: DocumentType;
  title?: string;
  description?: string;
  category?: string;
  tags?: string[];
  uploaded_date?: string;
  expiry_date?: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

export interface ExpiryAlert {
  document_id: string;
  document_type: DocumentType;
  title: string;
  expiry_date: string;
  days_until_expiry: number;
}

export interface ExpiryAlertResponse {
  expiring_soon: ExpiryAlert[];
  expired: ExpiryAlert[];
}

// ============================================================================
// API SERVICE
// ============================================================================

export const assetsService = {
  // Insurance Policies
  insurance: {
    list: async (params?: { policy_type?: PolicyType; limit?: number; offset?: number }): Promise<InsurancePolicyListResponse> => {
      return await apiClient.get('/assets/insurance', { params }) as InsurancePolicyListResponse;
    },

    get: async (id: string): Promise<InsurancePolicy> => {
      return await apiClient.get(`/assets/insurance/${id}`) as InsurancePolicy;
    },

    create: async (data: InsurancePolicyCreate): Promise<InsurancePolicy> => {
      return await apiClient.post('/assets/insurance', data) as InsurancePolicy;
    },

    update: async (id: string, data: InsurancePolicyUpdate): Promise<InsurancePolicy> => {
      return await apiClient.put(`/assets/insurance/${id}`, data) as InsurancePolicy;
    },

    delete: async (id: string): Promise<{ message: string; id: string }> => {
      return await apiClient.delete(`/assets/insurance/${id}`) as { message: string; id: string };
    },

    renewalAlerts: async (): Promise<RenewalAlertResponse> => {
      return await apiClient.get('/assets/insurance/alerts/renewals') as RenewalAlertResponse;
    },
  },

  // Documents
  documents: {
    list: async (params?: {
      document_type?: DocumentType;
      category?: string;
      tag?: string;
      search?: string;
      limit?: number;
      offset?: number;
    }): Promise<DocumentListResponse> => {
      return await apiClient.get('/assets/documents', { params }) as DocumentListResponse;
    },

    get: async (id: string): Promise<Document> => {
      return await apiClient.get(`/assets/documents/${id}`) as Document;
    },

    create: async (data: DocumentCreate): Promise<Document> => {
      return await apiClient.post('/assets/documents', data) as Document;
    },

    update: async (id: string, data: DocumentUpdate): Promise<Document> => {
      return await apiClient.put(`/assets/documents/${id}`, data) as Document;
    },

    delete: async (id: string): Promise<{ message: string; id: string }> => {
      return await apiClient.delete(`/assets/documents/${id}`) as { message: string; id: string };
    },

    expiryAlerts: async (): Promise<ExpiryAlertResponse> => {
      return await apiClient.get('/assets/documents/alerts/expiry') as ExpiryAlertResponse;
    },
  },
};
