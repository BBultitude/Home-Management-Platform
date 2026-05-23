import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Search,
  Plus,
  Filter,
  Ruler,
  Paintbrush,
  Wifi,
  Box,
  Car,
  Phone,
  Zap,
  Store,
  FileText,
  Edit,
  Trash2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { knowledgeService, type ArticleType, type KnowledgeArticle } from '@/services/knowledgeService';
import { ArticleForm } from './ArticleForm';

const ARTICLE_TYPE_CONFIG = {
  Measurement: { icon: Ruler, color: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300', label: 'Measurement' },
  Paint: { icon: Paintbrush, color: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300', label: 'Paint' },
  TechDevice: { icon: Wifi, color: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300', label: 'Tech Device' },
  StorageLocation: { icon: Box, color: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300', label: 'Storage' },
  Vehicle: { icon: Car, color: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300', label: 'Vehicle' },
  EmergencyContact: { icon: Phone, color: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300', label: 'Emergency Contact' },
  Appliance: { icon: Zap, color: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900 dark:text-cyan-300', label: 'Appliance' },
  Vendor: { icon: Store, color: 'bg-pink-100 text-pink-700 dark:bg-pink-900 dark:text-pink-300', label: 'Vendor' },
};

export default function KnowledgeBase() {
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<ArticleType | 'all'>('all');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingArticle, setEditingArticle] = useState<KnowledgeArticle | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [articleToDelete, setArticleToDelete] = useState<KnowledgeArticle | null>(null);
  const [searchTimeout, setSearchTimeout] = useState<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    loadArticles();
  }, [filterType]);

  useEffect(() => {
    // Debounce search
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    if (searchQuery.trim()) {
      const timeout = setTimeout(() => {
        performSearch();
      }, 300);
      setSearchTimeout(timeout);
    } else {
      loadArticles();
    }

    return () => {
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
    };
  }, [searchQuery]);

  const loadArticles = async () => {
    try {
      setLoading(true);
      const params = filterType === 'all' ? {} : { article_type: filterType };
      const response = await knowledgeService.articles.list(params);
      setArticles(response.articles);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to load articles');
    } finally {
      setLoading(false);
    }
  };

  const performSearch = async () => {
    try {
      setLoading(true);
      const searchParams = {
        query: searchQuery,
        article_types: filterType === 'all' ? undefined : [filterType],
      };
      const response = await knowledgeService.articles.search(searchParams);
      setArticles(response.articles);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to search articles');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateArticle = () => {
    setEditingArticle(null);
    setIsFormOpen(true);
  };

  const handleEditArticle = (article: KnowledgeArticle) => {
    setEditingArticle(article);
    setIsFormOpen(true);
  };

  const handleDeleteClick = (article: KnowledgeArticle) => {
    setArticleToDelete(article);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!articleToDelete) return;

    try {
      await knowledgeService.articles.delete(articleToDelete.id);
      toast.success('Article has been deleted successfully');
      loadArticles();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete article');
    } finally {
      setDeleteDialogOpen(false);
      setArticleToDelete(null);
    }
  };

  const handleFormSuccess = () => {
    setIsFormOpen(false);
    setEditingArticle(null);
    loadArticles();
  };

  const getArticleSummary = (article: KnowledgeArticle): string => {
    const { data } = article;
    switch (article.article_type) {
      case 'Measurement':
        return `${data.measurement_type}: ${data.value} ${data.unit} (${data.location})`;
      case 'Paint':
        return `${data.brand} ${data.color_name} - ${data.room_area}`;
      case 'TechDevice':
        return `${data.device_type}: ${data.brand_model} (${data.location})`;
      case 'StorageLocation':
        return `${data.storage_area} - ${data.category}`;
      case 'Vehicle':
        return `${data.year} ${data.make} ${data.model}`;
      case 'EmergencyContact':
        return `${data.name} - ${data.relationship_role} (${data.category})`;
      case 'Appliance':
        return `${data.appliance_type}: ${data.brand} (${data.location})`;
      case 'Vendor':
        return `${data.business_name} - ${data.service_type}`;
      default:
        return '';
    }
  };

  let articlesContent: React.ReactNode;
  if (loading) {
    articlesContent = (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        <p className="mt-4 text-muted-foreground">Loading articles...</p>
      </div>
    );
  } else if (articles.length === 0) {
    articlesContent = (
      <div className="text-center py-12 border-2 border-dashed rounded-lg">
        <BookOpen className="h-12 w-12 mx-auto text-muted-foreground" />
        <h3 className="mt-4 text-lg font-semibold">No Articles Found</h3>
        <p className="text-muted-foreground mt-2">
          {searchQuery ? 'Try adjusting your search terms' : 'Get started by creating your first article'}
        </p>
        {!searchQuery && (
          <Button onClick={handleCreateArticle} className="mt-4">
            <Plus className="h-4 w-4 mr-2" />
            Create Article
          </Button>
        )}
      </div>
    );
  } else {
    articlesContent = (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {articles.map((article) => {
          const config = ARTICLE_TYPE_CONFIG[article.article_type];
          const Icon = config.icon;

          return (
            <div
              key={article.id}
              className="border rounded-lg p-4 hover:shadow-lg transition-shadow bg-white dark:bg-white"
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`p-2 rounded-lg ${config.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEditArticle(article)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteClick(article)}
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </div>

              <h3 className="font-semibold text-lg mb-2 line-clamp-2">{article.title}</h3>
              <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                {getArticleSummary(article)}
              </p>

              <div className="flex flex-wrap gap-2 mb-3">
                {article.tags.slice(0, 3).map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
                {article.tags.length > 3 && (
                  <Badge variant="secondary" className="text-xs">
                    +{article.tags.length - 3} more
                  </Badge>
                )}
              </div>

              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{config.label}</span>
                {article.attachment_count > 0 && (
                  <div className="flex items-center gap-1">
                    <FileText className="h-3 w-3" />
                    <span>{article.attachment_count}</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Household Knowledge Base</h1>
        <p className="text-muted-foreground mt-2">
          Store and search household information, measurements, manuals, and contact details
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search articles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={filterType} onValueChange={(value) => setFilterType(value as ArticleType | 'all')}>
          <SelectTrigger className="w-full sm:w-[200px]">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue placeholder="Filter by type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {Object.entries(ARTICLE_TYPE_CONFIG).map(([type, config]) => (
              <SelectItem key={type} value={type}>
                {config.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button onClick={handleCreateArticle}>
          <Plus className="h-4 w-4 mr-2" />
          Add Article
        </Button>
      </div>

      {/* Articles Grid */}
      {articlesContent}

      {/* Article Form Dialog */}
      <ArticleForm
        open={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingArticle(null);
        }}
        onSuccess={handleFormSuccess}
        article={editingArticle}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-white dark:bg-white">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Article</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{articleToDelete?.title}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteConfirm} className="bg-red-500 hover:bg-red-600">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
