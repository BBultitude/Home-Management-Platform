import { useState, useEffect } from 'react';
import { projectsService, type Quote, type Project, type QuoteComparison } from '@/services/projectsService';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LoadingButton } from '@/components/ui/loading-button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/common/EmptyState';
import { PageLoader } from '@/components/common/PageLoader';
import { DatePicker } from '@/components/forms/DatePicker';
import { FileUploadInput } from '@/components/forms/FileUploadInput';
import { Plus, Edit, Trash2, CheckCircle2, BarChart3, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import { format, parseISO, differenceInDays } from 'date-fns';

export default function QuotesTab() {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [comparisons, setComparisons] = useState<QuoteComparison[]>([]);
  const [loading, setLoading] = useState(true);
  const [showComparison, setShowComparison] = useState(false);
  const [selectedProjectFilter, setSelectedProjectFilter] = useState<string>('all');
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedQuote, setSelectedQuote] = useState<Quote | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [formProjectId, setFormProjectId] = useState('');
  const [formContractorName, setFormContractorName] = useState('');
  const [formContactPhone, setFormContactPhone] = useState('');
  const [formContactEmail, setFormContactEmail] = useState('');
  const [formQuoteAmount, setFormQuoteAmount] = useState('');
  const [formQuoteDate, setFormQuoteDate] = useState<Date | undefined>(undefined);
  const [formExpiryDate, setFormExpiryDate] = useState<Date | undefined>(undefined);
  const [formScopeOfWork, setFormScopeOfWork] = useState('');
  const [formNotes, setFormNotes] = useState('');
  const [formDocumentId, setFormDocumentId] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [quotesResponse, projectsResponse] = await Promise.all([
        projectsService.quotes.listAll(),
        projectsService.projects.list(),
      ]);
      setQuotes(quotesResponse.quotes);
      setProjects(projectsResponse.projects);
    } catch (error) {
      console.error('Failed to load data:', error);
      toast.error('Failed to load quotes and projects');
    } finally {
      setLoading(false);
    }
  };

  const loadComparison = async () => {
    try {
      const response = await projectsService.quotes.compareAll();
      setComparisons(response.comparisons);
      setShowComparison(true);
    } catch (error) {
      console.error('Failed to load quote comparison:', error);
      toast.error('Failed to load quote comparison');
    }
  };

  const resetForm = () => {
    setFormProjectId('');
    setFormContractorName('');
    setFormContactPhone('');
    setFormContactEmail('');
    setFormQuoteAmount('');
    setFormQuoteDate(undefined);
    setFormExpiryDate(undefined);
    setFormScopeOfWork('');
    setFormNotes('');
    setFormDocumentId(null);
  };

  const openAddDialog = () => {
    resetForm();
    setAddDialogOpen(true);
  };

  const openEditDialog = (quote: Quote) => {
    setSelectedQuote(quote);
    setFormProjectId(quote.project_id);
    setFormContractorName(quote.contractor_name);
    setFormContactPhone(quote.contact_phone || '');
    setFormContactEmail(quote.contact_email || '');
    setFormQuoteAmount(quote.quote_amount.toString());
    setFormQuoteDate(parseISO(quote.quote_date));
    setFormExpiryDate(quote.expiry_date ? parseISO(quote.expiry_date) : undefined);
    setFormScopeOfWork(quote.scope_of_work || '');
    setFormNotes(quote.notes || '');
    setFormDocumentId(quote.document_id ? Number(quote.document_id) : null);
    setEditDialogOpen(true);
  };

  const openDeleteDialog = (quote: Quote) => {
    setSelectedQuote(quote);
    setDeleteDialogOpen(true);
  };

  const handleAdd = async () => {
    if (!formProjectId || !formContractorName.trim() || !formQuoteAmount || !formQuoteDate) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      setSubmitting(true);
      await projectsService.quotes.create(formProjectId, {
        contractor_name: formContractorName.trim(),
        contact_phone: formContactPhone.trim() || undefined,
        contact_email: formContactEmail.trim() || undefined,
        quote_amount: parseFloat(formQuoteAmount),
        quote_date: format(formQuoteDate, 'yyyy-MM-dd'),
        expiry_date: formExpiryDate ? format(formExpiryDate, 'yyyy-MM-dd') : undefined,
        scope_of_work: formScopeOfWork.trim() || undefined,
        notes: formNotes.trim() || undefined,
        document_id: formDocumentId || undefined,
      });
      toast.success('Quote created');
      setAddDialogOpen(false);
      loadData();
    } catch (error) {
      console.error('Failed to create quote:', error);
      toast.error('Failed to create quote');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = async () => {
    if (!selectedQuote || !formContractorName.trim() || !formQuoteAmount || !formQuoteDate) {
      return;
    }

    try {
      setSubmitting(true);
      await projectsService.quotes.update(selectedQuote.id, {
        contractor_name: formContractorName.trim(),
        contact_phone: formContactPhone.trim() || undefined,
        contact_email: formContactEmail.trim() || undefined,
        quote_amount: parseFloat(formQuoteAmount),
        quote_date: format(formQuoteDate, 'yyyy-MM-dd'),
        expiry_date: formExpiryDate ? format(formExpiryDate, 'yyyy-MM-dd') : undefined,
        scope_of_work: formScopeOfWork.trim() || undefined,
        notes: formNotes.trim() || undefined,
        document_id: formDocumentId || undefined,
      });
      toast.success('Quote updated');
      setEditDialogOpen(false);
      loadData();
    } catch (error) {
      console.error('Failed to update quote:', error);
      toast.error('Failed to update quote');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedQuote) return;

    try {
      setSubmitting(true);
      await projectsService.quotes.delete(selectedQuote.id);
      toast.success('Quote deleted');
      setDeleteDialogOpen(false);
      loadData();
    } catch (error) {
      console.error('Failed to delete quote:', error);
      toast.error('Failed to delete quote');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSelectQuote = async (quoteId: string) => {
    try {
      await projectsService.quotes.selectQuote(quoteId);
      toast.success('Quote selected');
      loadData();
    } catch (error) {
      console.error('Failed to select quote:', error);
      toast.error('Failed to select quote');
    }
  };

  const getExpiryBadge = (expiryDate: string | null) => {
    if (!expiryDate) {
      return <Badge variant="secondary">No expiry</Badge>;
    }

    const daysUntilExpiry = differenceInDays(parseISO(expiryDate), new Date());

    if (daysUntilExpiry < 0) {
      return (
        <Badge variant="destructive" className="flex items-center gap-1 w-fit">
          <AlertTriangle className="h-3 w-3" />
          Expired
        </Badge>
      );
    } else if (daysUntilExpiry <= 7) {
      return (
        <Badge variant="destructive" className="flex items-center gap-1 w-fit">
          <AlertTriangle className="h-3 w-3" />
          {daysUntilExpiry} days
        </Badge>
      );
    } else if (daysUntilExpiry <= 30) {
      return (
        <Badge className="bg-yellow-100 text-yellow-800 flex items-center gap-1 w-fit">
          <AlertTriangle className="h-3 w-3" />
          {daysUntilExpiry} days
        </Badge>
      );
    } else {
      return <Badge variant="secondary">{daysUntilExpiry} days</Badge>;
    }
  };

  const getProjectName = (projectId: string): string => {
    const project = projects.find(p => p.id === projectId);
    return project?.project_name || 'Unknown Project';
  };

  // Filter quotes
  const filteredQuotes = selectedProjectFilter === 'all'
    ? quotes
    : quotes.filter(q => q.project_id === selectedProjectFilter);

  // Calculate summary stats
  const totalQuotes = quotes.length;
  const selectedQuotes = quotes.filter(q => q.selected);
  const expiringQuotes = quotes.filter(q => {
    if (!q.expiry_date) return false;
    const days = differenceInDays(parseISO(q.expiry_date), new Date());
    return days >= 0 && days <= 30;
  });

  if (loading) {
    return <PageLoader />;
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Quotes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalQuotes}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              Selected Quotes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center gap-2">
              {selectedQuotes.length}
              <CheckCircle2 className="h-5 w-5 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              Expiring Soon
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center gap-2">
              {expiringQuotes.length}
              {expiringQuotes.length > 0 && (
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quotes Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <CardTitle>Contractor Quotes</CardTitle>
            <div className="flex gap-2">
              <Select value={selectedProjectFilter} onValueChange={setSelectedProjectFilter}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Filter by project" />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="all">All Projects</SelectItem>
                  {projects.map(project => (
                    <SelectItem key={project.id} value={project.id}>
                      {project.project_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button variant="outline" onClick={loadComparison}>
                <BarChart3 className="mr-2 h-4 w-4" />
                Compare
              </Button>
              <Button onClick={openAddDialog}>
                <Plus className="mr-2 h-4 w-4" />
                Add Quote
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredQuotes.length === 0 ? (
            <EmptyState
              title="No quotes"
              description="Add contractor quotes to compare and select the best option."
              action={{ label: 'Add Quote', onClick: openAddDialog }}
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Project</TableHead>
                  <TableHead>Contractor</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                  <TableHead>Quote Date</TableHead>
                  <TableHead>Expiry</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredQuotes.map((quote) => (
                  <TableRow key={quote.id}>
                    <TableCell className="font-medium">
                      {getProjectName(quote.project_id)}
                    </TableCell>
                    <TableCell>{quote.contractor_name}</TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {quote.contact_phone && <div>{quote.contact_phone}</div>}
                        {quote.contact_email && (
                          <div className="text-gray-500">{quote.contact_email}</div>
                        )}
                        {!quote.contact_phone && !quote.contact_email && '-'}
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-semibold">
                      ${quote.quote_amount.toLocaleString('en-AU', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </TableCell>
                    <TableCell>
                      {format(parseISO(quote.quote_date), 'dd MMM yyyy')}
                    </TableCell>
                    <TableCell>{getExpiryBadge(quote.expiry_date)}</TableCell>
                    <TableCell>
                      {quote.selected ? (
                        <Badge className="bg-green-100 text-green-800 flex items-center gap-1 w-fit">
                          <CheckCircle2 className="h-3 w-3" />
                          Selected
                        </Badge>
                      ) : (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleSelectQuote(quote.id)}
                          className="h-7 px-2 text-xs"
                        >
                          Select
                        </Button>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openEditDialog(quote)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openDeleteDialog(quote)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Add Dialog */}
      <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
        <DialogContent className="bg-white dark:bg-white max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add Quote</DialogTitle>
            <DialogDescription>
              Add a contractor quote for a project.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="project">Project *</Label>
              <Select value={formProjectId} onValueChange={setFormProjectId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select project" />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  {projects.map(project => (
                    <SelectItem key={project.id} value={project.id}>
                      {project.project_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="contractor">Contractor Name *</Label>
              <Input
                id="contractor"
                value={formContractorName}
                onChange={(e) => setFormContractorName(e.target.value)}
                placeholder="e.g., ABC Renovations"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="phone">Contact Phone</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formContactPhone}
                  onChange={(e) => setFormContactPhone(e.target.value)}
                  placeholder="0400 000 000"
                />
              </div>
              <div>
                <Label htmlFor="email">Contact Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formContactEmail}
                  onChange={(e) => setFormContactEmail(e.target.value)}
                  placeholder="contractor@example.com"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="amount">Quote Amount (AUD) *</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                min="0"
                value={formQuoteAmount}
                onChange={(e) => setFormQuoteAmount(e.target.value)}
                placeholder="0.00"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Quote Date *</Label>
                <DatePicker
                  date={formQuoteDate}
                  onDateChange={setFormQuoteDate}
                  placeholder="Select quote date"
                />
              </div>
              <div>
                <Label>Expiry Date</Label>
                <DatePicker
                  date={formExpiryDate}
                  onDateChange={setFormExpiryDate}
                  placeholder="Select expiry date"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="scope">Scope of Work</Label>
              <Textarea
                id="scope"
                value={formScopeOfWork}
                onChange={(e) => setFormScopeOfWork(e.target.value)}
                placeholder="What's included in this quote?"
                rows={3}
              />
            </div>
            <div>
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={formNotes}
                onChange={(e) => setFormNotes(e.target.value)}
                placeholder="Additional notes"
                rows={2}
              />
            </div>
            <FileUploadInput
              category="QUOTE"
              fileId={formDocumentId}
              onUploadSuccess={(id) => setFormDocumentId(id)}
              onDelete={() => setFormDocumentId(null)}
              label="Quote Document (optional)"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddDialogOpen(false)}>
              Cancel
            </Button>
            <LoadingButton onClick={handleAdd} loading={submitting}>
              Add Quote
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="bg-white dark:bg-white max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Quote</DialogTitle>
            <DialogDescription>
              Update quote details.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Project</Label>
              <Input value={getProjectName(formProjectId)} disabled />
            </div>
            <div>
              <Label htmlFor="edit-contractor">Contractor Name *</Label>
              <Input
                id="edit-contractor"
                value={formContractorName}
                onChange={(e) => setFormContractorName(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-phone">Contact Phone</Label>
                <Input
                  id="edit-phone"
                  type="tel"
                  value={formContactPhone}
                  onChange={(e) => setFormContactPhone(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="edit-email">Contact Email</Label>
                <Input
                  id="edit-email"
                  type="email"
                  value={formContactEmail}
                  onChange={(e) => setFormContactEmail(e.target.value)}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="edit-amount">Quote Amount (AUD) *</Label>
              <Input
                id="edit-amount"
                type="number"
                step="0.01"
                min="0"
                value={formQuoteAmount}
                onChange={(e) => setFormQuoteAmount(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Quote Date *</Label>
                <DatePicker
                  date={formQuoteDate}
                  onDateChange={setFormQuoteDate}
                  placeholder="Select quote date"
                />
              </div>
              <div>
                <Label>Expiry Date</Label>
                <DatePicker
                  date={formExpiryDate}
                  onDateChange={setFormExpiryDate}
                  placeholder="Select expiry date"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="edit-scope">Scope of Work</Label>
              <Textarea
                id="edit-scope"
                value={formScopeOfWork}
                onChange={(e) => setFormScopeOfWork(e.target.value)}
                rows={3}
              />
            </div>
            <div>
              <Label htmlFor="edit-notes">Notes</Label>
              <Textarea
                id="edit-notes"
                value={formNotes}
                onChange={(e) => setFormNotes(e.target.value)}
                rows={2}
              />
            </div>
            <FileUploadInput
              category="QUOTE"
              fileId={formDocumentId}
              onUploadSuccess={(id) => setFormDocumentId(id)}
              onDelete={() => setFormDocumentId(null)}
              label="Quote Document (optional)"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancel
            </Button>
            <LoadingButton onClick={handleEdit} loading={submitting}>
              Save Changes
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="bg-white dark:bg-white">
          <DialogHeader>
            <DialogTitle>Delete Quote</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this quote from "{selectedQuote && getProjectName(selectedQuote.project_id)}"?
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <LoadingButton
              onClick={handleDelete}
              loading={submitting}
              variant="destructive"
            >
              Delete
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Quote Comparison Dialog */}
      <Dialog open={showComparison} onOpenChange={setShowComparison}>
        <DialogContent className="bg-white dark:bg-white max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Quote Comparison</DialogTitle>
            <DialogDescription>
              Compare contractor quotes across all projects.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            {comparisons.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No quotes to compare</p>
            ) : (
              comparisons.map(comparison => (
                <Card key={comparison.project_id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{comparison.project_name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-500">Quotes</p>
                        <p className="text-xl font-bold">{comparison.quote_count}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Lowest</p>
                        <p className="text-xl font-bold text-green-600">
                          ${comparison.lowest_quote.toLocaleString('en-AU', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Highest</p>
                        <p className="text-xl font-bold text-red-600">
                          ${comparison.highest_quote.toLocaleString('en-AU', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Average</p>
                        <p className="text-xl font-bold">
                          ${comparison.average_quote.toLocaleString('en-AU', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}
                        </p>
                      </div>
                    </div>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Contractor</TableHead>
                          <TableHead className="text-right">Amount</TableHead>
                          <TableHead>Status</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {comparison.quotes.map(quote => (
                          <TableRow key={quote.id}>
                            <TableCell>{quote.contractor_name}</TableCell>
                            <TableCell className="text-right font-semibold">
                              ${quote.quote_amount.toLocaleString('en-AU', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              })}
                            </TableCell>
                            <TableCell>
                              {quote.selected && (
                                <Badge className="bg-green-100 text-green-800 flex items-center gap-1 w-fit">
                                  <CheckCircle2 className="h-3 w-3" />
                                  Selected
                                </Badge>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
          <DialogFooter>
            <Button onClick={() => setShowComparison(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
