import { apiClient } from '@/lib/api';

export type FileCategory =
  | 'INSURANCE'
  | 'QUOTE'
  | 'UTILITY'
  | 'KNOWLEDGE'
  | 'TAX'
  | 'PROJECT'
  | 'ASSET'
  | 'OTHER';

export interface FileMetadata {
  id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  mime_type: string;
  file_size: number;
  category: FileCategory;
  description?: string;
  uploaded_at: string;
}

export interface FileUploadResponse {
  id: number;
  filename: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  category: FileCategory;
  description?: string;
  uploaded_at: string;
  message: string;
}

export interface StorageQuotaResponse {
  storage_used_bytes: number;
  storage_limit_bytes: number;
  storage_used_mb: number;
  storage_limit_mb: number;
  storage_percentage: number;
  files_count: number;
}

export const fileService = {
  upload: async (file: File, category: FileCategory): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category.toLowerCase());

    return await apiClient.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }) as FileUploadResponse;
  },

  get: async (id: number): Promise<FileMetadata> => {
    return await apiClient.get(`/files/${id}`) as FileMetadata;
  },

  download: async (id: number): Promise<Blob> => {
    return await apiClient.get(`/files/${id}/download`, {
      responseType: 'blob',
    }) as Blob;
  },

  delete: async (id: number): Promise<{ message: string }> => {
    return await apiClient.delete(`/files/${id}`) as { message: string };
  },

  list: async (category?: FileCategory): Promise<{ files: FileMetadata[] }> => {
    return await apiClient.get('/files', {
      params: category ? { category: category.toLowerCase() } : undefined,
    }) as { files: FileMetadata[] };
  },

  getQuota: async (): Promise<StorageQuotaResponse> => {
    return await apiClient.get('/files/storage/quota') as StorageQuotaResponse;
  },
};
