import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, FileText, AlertTriangle, Calendar, Tag, Search, File, Receipt, ShieldCheck, BookOpen, Award, Scale, Stethoscope, Wallet, Download } from 'lucide-react';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/common/EmptyState';
import { PageLoader } from '@/components/common/PageLoader';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { LoadingButton } from '@/components/ui/loading-button';
import { DatePicker } from '@/components/forms/DatePicker';
import { FileUploadInput } from '@/components/forms/FileUploadInput';
import { assetsService } from '@/services/assetsService';
import type { Document, DocumentCreate, DocumentType, InsurancePolicy } from '@/services/assetsService';
import { fileService } from '@/services/fileService';
import { getErrorMessage } from '@/lib/errorMessages';
import { toast } from 'sonner';

export default function DocumentsTab() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [insurancePolicies, setInsurancePolicies] = useState<InsurancePolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingDocument, setEditingDocument] = useState<Document | null>(null);
  const [deleteDocument, setDeleteDocument] = useState<Document | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Filter state
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Form state
  const [formType, setFormType] = useState<DocumentType>('Contract');
  const [formTitle, setFormTitle] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formCategory, setFormCategory] = useState('');
  const [formTags, setFormTags] = useState('');
  const [formUploadedDate, setFormUploadedDate] = useState<Date | undefined>(new Date());
  const [formExpiryDate, setFormExpiryDate] = useState<Date | undefined>(undefined);
  const [formFileId, setFormFileId] = useState('');

  // Fetch documents
  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (typeFilter !== 'all') {
        params.document_type = typeFilter;
      }
      if (searchQuery) {
        params.search = searchQuery;
      }

      const [docsResponse, insuranceResponse] = await Promise.all([
        assetsService.documents.list(params),
        assetsService.insurance.list(),
      ]);
      setDocuments(docsResponse.documents);
      setInsurancePolicies(
        insuranceResponse.policies.filter((p) => p.document_id !== null)
      );
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [typeFilter, searchQuery]);

  const handleDownloadInsuranceDoc = async (policy: InsurancePolicy) => {
    if (!policy.document_id) return;
    try {
      const blob = await fileService.download(parseInt(policy.document_id));
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${policy.provider}_${policy.policy_type}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch {
      toast.error('Failed to download file');
    }
  };

  const resetForm = () => {
    setFormType('Contract');
    setFormTitle('');
    setFormDescription('');
    setFormCategory('');
    setFormTags('');
    setFormUploadedDate(new Date());
    setFormExpiryDate(undefined);
    setFormFileId('');
  };

  const openAddDialog = () => {
    resetForm();
    setEditingDocument(null);
    setShowDialog(true);
  };

  const openEditDialog = (document: Document) => {
    setEditingDocument(document);
    setFormType(document.document_type);
    setFormTitle(document.title);
    setFormDescription(document.description || '');
    setFormCategory(document.category || '');
    setFormTags(document.tags.join(', '));
    setFormUploadedDate(new Date(document.uploaded_date));
    setFormExpiryDate(document.expiry_date ? new Date(document.expiry_date) : undefined);
    setFormFileId(document.file_id);
    setShowDialog(true);
  };

  const handleSubmit = async () => {
    if (!formTitle || !formFileId) {
      toast.error('Please fill in all required fields');
      return;
    }

    setSubmitting(true);
    try {
      const tags = formTags
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0);

      const data: DocumentCreate = {
        document_type: formType,
        title: formTitle,
        description: formDescription || undefined,
        category: formCategory || undefined,
        tags: tags.length > 0 ? tags : undefined,
        uploaded_date: formUploadedDate ? format(formUploadedDate, 'yyyy-MM-dd') : undefined,
        expiry_date: formExpiryDate ? format(formExpiryDate, 'yyyy-MM-dd') : undefined,
        file_id: parseInt(formFileId),
      };

      if (editingDocument) {
        await assetsService.documents.update(editingDocument.id, data);
        toast.success('Document updated');
      } else {
        await assetsService.documents.create(data);
        toast.success('Document created');
      }

      setShowDialog(false);
      fetchDocuments();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteDocument) return;

    try {
      await assetsService.documents.delete(deleteDocument.id);
      toast.success('Document deleted');
      setDeleteDocument(null);
      fetchDocuments();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const getDocumentIcon = (type: DocumentType) => {
    const icons = {
      'Contract': FileText,
      'Receipt': Receipt,
      'Warranty': ShieldCheck,
      'Manual': BookOpen,
      'Certificate': Award,
      'Legal': Scale,
      'Medical': Stethoscope,
      'Financial': Wallet,
      'Other': File,
    };
    const Icon = icons[type];
    return <Icon className="h-4 w-4" />;
  };

  const getDocumentBadge = (type: DocumentType) => {
    const colors = {
      'Contract': 'bg-blue-100 text-blue-800',
      'Receipt': 'bg-green-100 text-green-800',
      'Warranty': 'bg-purple-100 text-purple-800',
      'Manual': 'bg-yellow-100 text-yellow-800',
      'Certificate': 'bg-pink-100 text-pink-800',
      'Legal': 'bg-red-100 text-red-800',
      'Medical': 'bg-cyan-100 text-cyan-800',
      'Financial': 'bg-indigo-100 text-indigo-800',
      'Other': 'bg-gray-100 text-gray-800',
    };
    return (
      <Badge className={colors[type]} variant="secondary">
        <span className="flex items-center gap-1">
          {getDocumentIcon(type)}
          {type}
        </span>
      </Badge>
    );
  };

  const getExpiryBadge = (expiryDate: string | null) => {
    if (!expiryDate) {
      return <Badge variant="secondary">No expiry</Badge>;
    }

    const today = new Date();
    const expiry = new Date(expiryDate);
    const daysUntil = Math.floor((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    if (daysUntil < 0) {
      return <Badge variant="destructive">Expired</Badge>;
    } else if (daysUntil <= 7) {
      return <Badge variant="destructive" className="flex items-center gap-1">
        <AlertTriangle className="h-3 w-3" />
        {daysUntil} days
      </Badge>;
    } else if (daysUntil <= 30) {
      return <Badge className="bg-yellow-100 text-yellow-800 flex items-center gap-1">
        <AlertTriangle className="h-3 w-3" />
        {daysUntil} days
      </Badge>;
    } else {
      return <Badge variant="secondary">{daysUntil} days</Badge>;
    }
  };

  if (loading) {
    return <PageLoader message="Loading documents..." />;
  }

  return (
    <div className="space-y-6">
      {/* Filters and Actions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Filters</CardTitle>
            </div>
            <Button onClick={openAddDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Add Document
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Document Type</Label>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="bg-white dark:bg-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="Contract">📄 Contract</SelectItem>
                  <SelectItem value="Receipt">🧾 Receipt</SelectItem>
                  <SelectItem value="Warranty">🛡️ Warranty</SelectItem>
                  <SelectItem value="Manual">📖 Manual</SelectItem>
                  <SelectItem value="Certificate">🏆 Certificate</SelectItem>
                  <SelectItem value="Legal">⚖️ Legal</SelectItem>
                  <SelectItem value="Medical">🩺 Medical</SelectItem>
                  <SelectItem value="Financial">💼 Financial</SelectItem>
                  <SelectItem value="Other">📁 Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by title, category, or tags..."
                  className="pl-9 bg-white dark:bg-white"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Documents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{documents.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Expiring Soon (30 days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {documents.filter(d => {
                if (!d.expiry_date) return false;
                const days = Math.floor((new Date(d.expiry_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
                return days >= 0 && days <= 30;
              }).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Expired
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {documents.filter(d => {
                if (!d.expiry_date) return false;
                return new Date(d.expiry_date) < new Date();
              }).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Documents Table */}
      {documents.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No documents"
          description="Add your first document to start organizing important household files."
          action={{
            label: 'Add Document',
            onClick: openAddDialog
          }}
        />
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Documents</CardTitle>
            <CardDescription>
              {documents.length} {documents.length === 1 ? 'document' : 'documents'} found
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Type</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Tags</TableHead>
                    <TableHead>Uploaded</TableHead>
                    <TableHead>Expiry</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {documents.map((document) => (
                    <TableRow key={document.id}>
                      <TableCell>{getDocumentBadge(document.document_type)}</TableCell>
                      <TableCell className="font-medium">{document.title}</TableCell>
                      <TableCell className="text-gray-500">
                        {document.category || '—'}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {document.tags.length > 0 ? (
                            document.tags.slice(0, 2).map((tag) => (
                              <Badge
                                key={tag}
                                variant="outline"
                                className="text-xs"
                              >
                                <Tag className="h-3 w-3 mr-1" />
                                {tag}
                              </Badge>
                            ))
                          ) : (
                            <span className="text-gray-400 text-sm">—</span>
                          )}
                          {document.tags.length > 2 && (
                            <Badge variant="outline" className="text-xs">
                              +{document.tags.length - 2}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm text-gray-500">
                          <Calendar className="h-3 w-3" />
                          {format(new Date(document.uploaded_date), 'MMM dd, yyyy')}
                        </div>
                      </TableCell>
                      <TableCell>{getExpiryBadge(document.expiry_date)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openEditDialog(document)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setDeleteDocument(document)}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Insurance Documents Section */}
      {insurancePolicies.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Insurance Documents</CardTitle>
            <CardDescription>
              Documents attached to insurance policies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Type</TableHead>
                    <TableHead>Policy</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {insurancePolicies.map((policy) => (
                    <TableRow key={policy.id}>
                      <TableCell>
                        <Badge className="bg-purple-100 text-purple-800" variant="secondary">
                          <span className="flex items-center gap-1">
                            <ShieldCheck className="h-4 w-4" />
                            Insurance
                          </span>
                        </Badge>
                      </TableCell>
                      <TableCell className="font-medium">{policy.provider}</TableCell>
                      <TableCell className="text-gray-500">{policy.policy_type}</TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownloadInsuranceDoc(policy)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="bg-white dark:bg-white max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingDocument ? 'Edit Document' : 'Add Document'}
            </DialogTitle>
            <DialogDescription>
              {editingDocument
                ? 'Update document details'
                : 'Create a new document record'}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="type">Document Type *</Label>
                <Select value={formType} onValueChange={(value) => setFormType(value as DocumentType)}>
                  <SelectTrigger id="type" className="bg-white dark:bg-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white dark:bg-white">
                    <SelectItem value="Contract">📄 Contract</SelectItem>
                    <SelectItem value="Receipt">🧾 Receipt</SelectItem>
                    <SelectItem value="Warranty">🛡️ Warranty</SelectItem>
                    <SelectItem value="Manual">📖 Manual</SelectItem>
                    <SelectItem value="Certificate">🏆 Certificate</SelectItem>
                    <SelectItem value="Legal">⚖️ Legal</SelectItem>
                    <SelectItem value="Medical">🩺 Medical</SelectItem>
                    <SelectItem value="Financial">💼 Financial</SelectItem>
                    <SelectItem value="Other">📁 Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  value={formTitle}
                  onChange={(e) => setFormTitle(e.target.value)}
                  placeholder="e.g., Home Insurance Policy"
                  className="bg-white dark:bg-white"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                placeholder="Optional description..."
                className="bg-white dark:bg-white"
                rows={2}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  value={formCategory}
                  onChange={(e) => setFormCategory(e.target.value)}
                  placeholder="e.g., Insurance, Appliances"
                  className="bg-white dark:bg-white"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tags">Tags (comma-separated)</Label>
                <Input
                  id="tags"
                  value={formTags}
                  onChange={(e) => setFormTags(e.target.value)}
                  placeholder="e.g., important, warranty, 2024"
                  className="bg-white dark:bg-white"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Uploaded Date</Label>
                <DatePicker
                  date={formUploadedDate}
                  onDateChange={setFormUploadedDate}
                  placeholder="Select upload date"
                />
              </div>

              <div className="space-y-2">
                <Label>Expiry Date (optional)</Label>
                <DatePicker
                  date={formExpiryDate}
                  onDateChange={setFormExpiryDate}
                  placeholder="No expiry"
                />
              </div>
            </div>

            <FileUploadInput
              category="ASSET"
              fileId={formFileId ? parseInt(formFileId) : null}
              onUploadSuccess={(id) => setFormFileId(id.toString())}
              onDelete={() => setFormFileId('')}
              label="Document File"
              required
            />
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>
              Cancel
            </Button>
            <LoadingButton onClick={handleSubmit} loading={submitting}>
              {editingDocument ? 'Update' : 'Create'}
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      {deleteDocument && (
        <ConfirmDialog
          open={!!deleteDocument}
          onOpenChange={(open) => !open && setDeleteDocument(null)}
          onConfirm={handleDelete}
          title="Delete Document?"
          description={`Are you sure you want to delete "${deleteDocument.title}"? This will also delete the associated file. This action cannot be undone.`}
          confirmText="Delete"
          variant="destructive"
        />
      )}
    </div>
  );
}
