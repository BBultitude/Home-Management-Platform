import { apiClient } from '@/lib/api';

export type ArticleType =
  | 'Measurement'
  | 'Paint'
  | 'TechDevice'
  | 'StorageLocation'
  | 'Vehicle'
  | 'EmergencyContact'
  | 'Appliance'
  | 'Vendor';

export interface KnowledgeArticle {
  id: string;
  article_type: ArticleType;
  title: string;
  data: Record<string, any>;
  tags: string[];
  created_by: string | null;
  created_at: string;
  updated_at: string;
  attachment_count: number;
}

export interface KnowledgeArticleCreate {
  article_type: ArticleType;
  title: string;
  data: Record<string, any>;
  tags?: string[];
  attachment_ids?: string[];
}

export interface KnowledgeArticleUpdate {
  title?: string;
  data?: Record<string, any>;
  tags?: string[];
}

export interface KnowledgeListResponse {
  articles: KnowledgeArticle[];
  total: number;
}

export interface SearchRequest {
  query: string;
  article_types?: ArticleType[];
  tags?: string[];
  limit?: number;
}

export interface AttachmentInfo {
  id: string;
  article_id: string;
  file_id: string;
}

export const knowledgeService = {
  articles: {
    list: async (params?: { article_type?: ArticleType; tags?: string[]; limit?: number; offset?: number }): Promise<KnowledgeListResponse> => {
      return await apiClient.get('/knowledge', { params }) as KnowledgeListResponse;
    },

    search: async (request: SearchRequest): Promise<KnowledgeListResponse> => {
      return await apiClient.post('/knowledge/search', request) as KnowledgeListResponse;
    },

    get: async (id: string): Promise<KnowledgeArticle> => {
      return await apiClient.get(`/knowledge/${id}`) as KnowledgeArticle;
    },

    create: async (data: KnowledgeArticleCreate): Promise<KnowledgeArticle> => {
      return await apiClient.post('/knowledge', data) as KnowledgeArticle;
    },

    update: async (id: string, data: KnowledgeArticleUpdate): Promise<KnowledgeArticle> => {
      return await apiClient.put(`/knowledge/${id}`, data) as KnowledgeArticle;
    },

    delete: async (id: string): Promise<{ message: string; id: string }> => {
      return await apiClient.delete(`/knowledge/${id}`) as { message: string; id: string };
    },
  },

  attachments: {
    add: async (articleId: string, fileIds: string[]): Promise<{ message: string; attachments: AttachmentInfo[] }> => {
      return await apiClient.post(`/knowledge/${articleId}/attachments`, { file_ids: fileIds }) as { message: string; attachments: AttachmentInfo[] };
    },

    list: async (articleId: string): Promise<{ attachments: AttachmentInfo[] }> => {
      return await apiClient.get(`/knowledge/${articleId}/attachments`) as { attachments: AttachmentInfo[] };
    },

    remove: async (articleId: string, fileId: string): Promise<{ message: string }> => {
      return await apiClient.delete(`/knowledge/${articleId}/attachments/${fileId}`) as { message: string };
    },
  },
};
