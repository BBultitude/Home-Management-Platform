/**
 * Projects & Tasks Service
 * API client for priority items, projects, and contractor quotes
 */

import { apiClient } from '@/lib/api';

// ============================================================================
// PRIORITY ITEMS (Repair Prioritization)
// ============================================================================

export type PriorityStatus = 'Pending' | 'ConvertedToProject' | 'Done' | 'Dismissed';

export interface PriorityItem {
  id: string; // UUID
  description: string;
  cost: number;
  severity: number; // 1-5
  frequency: number; // 1-5
  benefit_score: number; // Auto-calculated: severity + frequency (2-10)
  cost_score: number; // Auto-calculated: log10(cost) + 1 (1-5)
  net_score: number; // Auto-calculated: benefit - cost_score (-3 to 9)
  status: PriorityStatus;
  project_id: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface PriorityItemCreate {
  description: string;
  cost: number;
  severity: number; // 1-5
  frequency: number; // 1-5
}

export interface PriorityItemUpdate {
  description?: string;
  cost?: number;
  severity?: number;
  frequency?: number;
  status?: PriorityStatus;
}

export interface PriorityItemListResponse {
  items: PriorityItem[];
  total: number;
}

export interface ConvertToProjectRequest {
  project_name: string;
  description?: string;
  budget?: number;
}

// ============================================================================
// PROJECTS
// ============================================================================

export type ProjectStatus = 'Planned' | 'Approved' | 'InProgress' | 'Completed' | 'Cancelled';

export interface Project {
  id: string; // UUID
  project_name: string;
  description: string | null;
  priority_item_id: string | null;
  status: ProjectStatus;
  start_date: string | null; // ISO date
  completion_date: string | null; // ISO date
  budget: number | null;
  actual_cost: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  project_name: string;
  description?: string;
  status?: ProjectStatus;
  start_date?: string; // YYYY-MM-DD
  completion_date?: string;
  budget?: number;
  actual_cost?: number;
  notes?: string;
}

export interface ProjectUpdate {
  project_name?: string;
  description?: string;
  status?: ProjectStatus;
  start_date?: string;
  completion_date?: string;
  budget?: number;
  actual_cost?: number;
  notes?: string;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

// ============================================================================
// QUOTES
// ============================================================================

export interface Quote {
  id: string; // UUID
  project_id: string;
  contractor_name: string;
  contact_phone: string | null;
  contact_email: string | null;
  quote_amount: number;
  quote_date: string; // ISO date
  expiry_date: string | null; // ISO date
  scope_of_work: string | null;
  selected: boolean;
  document_id: string | null;
  notes: string | null;
  created_at: string;
}

export interface QuoteCreate {
  project_id: string;
  contractor_name: string;
  contact_phone?: string;
  contact_email?: string;
  quote_amount: number;
  quote_date: string; // YYYY-MM-DD
  expiry_date?: string;
  scope_of_work?: string;
  selected?: boolean;
  document_id?: number;
  notes?: string;
}

export interface QuoteUpdate {
  contractor_name?: string;
  contact_phone?: string;
  contact_email?: string;
  quote_amount?: number;
  quote_date?: string;
  expiry_date?: string;
  scope_of_work?: string;
  selected?: boolean;
  document_id?: number;
  notes?: string;
}

export interface QuoteListResponse {
  quotes: Quote[];
  total: number;
}

export interface QuoteComparison {
  project_id: string;
  project_name: string;
  quote_count: number;
  lowest_quote: number;
  highest_quote: number;
  average_quote: number;
  selected_quote_id: string | null;
  quotes: Quote[];
}

export interface QuoteComparisonResponse {
  comparisons: QuoteComparison[];
}

// ============================================================================
// API SERVICE
// ============================================================================

export const projectsService = {
  // Priority Items
  priorities: {
    list: async (params?: { status?: PriorityStatus; limit?: number; offset?: number }): Promise<PriorityItemListResponse> => {
      return await apiClient.get('/projects/priorities', { params }) as PriorityItemListResponse;
    },

    get: async (id: string): Promise<PriorityItem> => {
      return await apiClient.get(`/projects/priorities/${id}`) as PriorityItem;
    },

    create: async (data: PriorityItemCreate): Promise<PriorityItem> => {
      return await apiClient.post('/projects/priorities', data) as PriorityItem;
    },

    update: async (id: string, data: PriorityItemUpdate): Promise<PriorityItem> => {
      return await apiClient.put(`/projects/priorities/${id}`, data) as PriorityItem;
    },

    delete: async (id: string): Promise<{ message: string; id: string }> => {
      return await apiClient.delete(`/projects/priorities/${id}`) as { message: string; id: string };
    },

    convertToProject: async (id: string, data: ConvertToProjectRequest): Promise<Project> => {
      return await apiClient.post(`/projects/priorities/${id}/convert`, data) as Project;
    },
  },

  // Projects
  projects: {
    list: async (params?: { status?: ProjectStatus; limit?: number; offset?: number }): Promise<ProjectListResponse> => {
      return await apiClient.get('/projects', { params }) as ProjectListResponse;
    },

    get: async (id: string): Promise<Project> => {
      return await apiClient.get(`/projects/${id}`) as Project;
    },

    create: async (data: ProjectCreate): Promise<Project> => {
      return await apiClient.post('/projects', data) as Project;
    },

    update: async (id: string, data: ProjectUpdate): Promise<Project> => {
      return await apiClient.put(`/projects/${id}`, data) as Project;
    },

    delete: async (id: string): Promise<{ message: string; id: string }> => {
      return await apiClient.delete(`/projects/${id}`) as { message: string; id: string };
    },
  },

  // Quotes
  quotes: {
    // List quotes for a specific project
    listForProject: async (projectId: string): Promise<QuoteListResponse> => {
      return await apiClient.get(`/projects/${projectId}/quotes`) as QuoteListResponse;
    },

    // List quotes across all projects (client-side aggregation)
    listAll: async (): Promise<QuoteListResponse> => {
      // Get all projects first
      const projectsResponse = await apiClient.get('/projects') as ProjectListResponse;

      // Fetch quotes for each project
      const allQuotes: Quote[] = [];
      for (const project of projectsResponse.projects) {
        try {
          const quotesResponse = await apiClient.get(`/projects/${project.id}/quotes`) as QuoteListResponse;
          allQuotes.push(...quotesResponse.quotes);
        } catch (error) {
          // Skip projects with no quotes or errors
          console.warn(`Failed to fetch quotes for project ${project.id}:`, error);
        }
      }

      return {
        quotes: allQuotes,
        total: allQuotes.length,
      };
    },

    get: async (id: string): Promise<Quote> => {
      return await apiClient.get(`/projects/quotes/${id}`) as Quote;
    },

    create: async (projectId: string, data: Omit<QuoteCreate, 'project_id'>): Promise<Quote> => {
      // Include project_id in body for schema validation (backend uses URL param anyway)
      return await apiClient.post(`/projects/${projectId}/quotes`, {
        ...data,
        project_id: projectId,
      }) as Quote;
    },

    update: async (id: string, data: QuoteUpdate): Promise<Quote> => {
      return await apiClient.put(`/projects/quotes/${id}`, data) as Quote;
    },

    delete: async (id: string): Promise<{ message: string; id: string }> => {
      return await apiClient.delete(`/projects/quotes/${id}`) as { message: string; id: string };
    },

    // Select quote by updating it with selected: true
    selectQuote: async (id: string): Promise<Quote> => {
      return await apiClient.put(`/projects/quotes/${id}`, { selected: true }) as Quote;
    },

    // Get comparison for a specific project
    compareForProject: async (projectId: string): Promise<QuoteComparison> => {
      return await apiClient.get(`/projects/${projectId}/quotes/compare`) as QuoteComparison;
    },

    // Get comparisons across all projects (client-side aggregation)
    compareAll: async (): Promise<QuoteComparisonResponse> => {
      const projectsResponse = await apiClient.get('/projects') as ProjectListResponse;

      const comparisons: QuoteComparison[] = [];
      for (const project of projectsResponse.projects) {
        try {
          const comparison = await apiClient.get(`/projects/${project.id}/quotes/compare`) as QuoteComparison;
          if (comparison.quote_count > 0) {
            comparisons.push(comparison);
          }
        } catch (error) {
          // Skip projects with no quotes or errors
          console.warn(`Failed to fetch comparison for project ${project.id}:`, error);
        }
      }

      return { comparisons };
    },
  },
};
