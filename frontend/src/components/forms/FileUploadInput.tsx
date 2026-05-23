import React, { useState, useRef, useEffect } from 'react';
import { Upload, X, Download, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import { fileService, type FileCategory, type FileMetadata } from '@/services/fileService';

type FileUploadInputProps = Readonly<{
  category: FileCategory;
  fileId?: number | null;
  onUploadSuccess: (fileId: number) => void;
  onDelete?: () => void;
  label?: string;
  required?: boolean;
  disabled?: boolean;
}>

const ALLOWED_TYPES = [
  'application/pdf',
  'image/png',
  'image/jpeg',
  'image/jpg',
  'image/gif',
  'image/webp',
  'text/plain',
  'text/csv',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
];

const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

const getFileIcon = (mimeType: string) => {
  if (mimeType.startsWith('image/')) return '🖼️';
  if (mimeType === 'application/pdf') return '📄';
  if (mimeType.includes('spreadsheet') || mimeType === 'text/csv') return '📊';
  return '📁';
};

export const FileUploadInput: React.FC<FileUploadInputProps> = ({
  category,
  fileId,
  onUploadSuccess,
  onDelete,
  label,
  required = false,
  disabled = false,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState<FileMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (fileId && fileId !== currentFile?.id) {
      loadFileMetadata(fileId);
    } else if (!fileId) {
      setCurrentFile(null);
    }
  }, [fileId]);

  const loadFileMetadata = async (id: number) => {
    try {
      const metadata = await fileService.get(id);
      setCurrentFile(metadata);
      setError(null);
    } catch (err) {
      console.error('Failed to load file metadata:', err);
      setError('Failed to load file information');
    }
  };

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return `File type not allowed. Allowed types: PDF, PNG, JPG, GIF, WEBP, TXT, CSV, XLSX`;
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds 20MB limit. Your file is ${formatFileSize(file.size)}`;
    }
    return null;
  };

  const handleFileUpload = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      toast.error(validationError);
      return;
    }

    setError(null);
    setIsUploading(true);
    setUploadProgress(0);

    // Simulate progress (real progress would need XMLHttpRequest)
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => Math.min(prev + 10, 90));
    }, 200);

    try {
      const response = await fileService.upload(file, category);
      clearInterval(progressInterval);
      setUploadProgress(100);

      await loadFileMetadata(response.id);
      onUploadSuccess(response.id);

      toast.success(`${file.name} uploaded successfully`);
    } catch (err: any) {
      clearInterval(progressInterval);
      let errorMessage = 'Failed to upload file';

      // Handle different error response formats
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          // Pydantic validation errors
          errorMessage = detail.map((e: any) => e.msg || e.message).join(', ');
        } else if (typeof detail === 'object') {
          errorMessage = detail.msg || detail.message || JSON.stringify(detail);
        }
      }

      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleDelete = async () => {
    if (!currentFile) return;

    try {
      await fileService.delete(currentFile.id);
      setCurrentFile(null);
      if (onDelete) {
        onDelete();
      }
      toast.success('File removed successfully');
    } catch (err: any) {
      let errorMessage = 'Failed to delete file';
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        errorMessage = typeof detail === 'string' ? detail : (detail.msg || detail.message || 'Failed to delete file');
      }
      toast.error(errorMessage);
    }
  };

  const handleDownload = async () => {
    if (!currentFile) return;

    try {
      const blob = await fileService.download(currentFile.id);
      const url = globalThis.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = currentFile.original_filename;
      document.body.appendChild(a);
      a.click();
      globalThis.URL.revokeObjectURL(url);
      a.remove();
    } catch (err) {
      console.error('Failed to download file:', err);
      toast.error('Failed to download file');
    }
  };

  if (currentFile) {
    return (
      <div className="space-y-2">
        {label && (
          <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
            {label} {required && <span className="text-red-500">*</span>}
          </label>
        )}
        <div className="flex items-center gap-3 p-4 border rounded-lg bg-gray-50 dark:bg-gray-900">
          <div className="text-2xl">{getFileIcon(currentFile.mime_type)}</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{currentFile.original_filename}</p>
            <p className="text-xs text-muted-foreground">
              {formatFileSize(currentFile.file_size)} • {currentFile.mime_type.split('/')[1].toUpperCase()}
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleDownload}
            >
              <Download className="h-4 w-4" />
            </Button>
            {!disabled && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleDelete}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {label && (
        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}

      <div
        role="button"
        tabIndex={disabled ? -1 : 0}
        className={`
          border-2 border-dashed rounded-lg p-6 text-center transition-colors
          ${isDragging ? 'border-blue-500 bg-blue-50 dark:bg-blue-950' : 'border-gray-300 hover:border-blue-400'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.currentTarget.click(); } }}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileInputChange}
          disabled={disabled}
          accept={ALLOWED_TYPES.join(',')}
        />

        {isUploading ? (
          <div className="space-y-3">
            <Loader2 className="h-10 w-10 mx-auto animate-spin text-blue-500" />
            <p className="text-sm text-muted-foreground">Uploading...</p>
            <Progress value={uploadProgress} className="w-full" />
          </div>
        ) : (
          <div className="space-y-2">
            <Upload className="h-10 w-10 mx-auto text-gray-400" />
            <div>
              <p className="text-sm font-medium">
                {isDragging ? 'Drop file here' : 'Drag & drop file here'}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                or click to browse
              </p>
            </div>
            <p className="text-xs text-muted-foreground">
              PDF, PNG, JPG, GIF, WEBP, TXT, CSV, XLSX (max 20MB)
            </p>
          </div>
        )}
      </div>

      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  );
};
