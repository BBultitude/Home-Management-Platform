import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { DatePicker } from '@/components/forms/DatePicker';
import { EmptyState } from '@/components/common/EmptyState';
import { PageLoader } from '@/components/common/PageLoader';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { LoadingButton } from '@/components/ui/loading-button';
import { taxService } from '@/services/taxService';
import type { WFHEntry, WFHEntryCreate } from '@/services/taxService';
import { getErrorMessage } from '@/lib/errorMessages';
import { toast } from 'sonner';

interface WFHTabProps {
  financialYear: string;
}

export function WFHTab({ financialYear }: WFHTabProps) {
  const [entries, setEntries] = useState<WFHEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingEntry, setEditingEntry] = useState<WFHEntry | null>(null);
  const [deleteEntry, setDeleteEntry] = useState<WFHEntry | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [formDate, setFormDate] = useState<Date | undefined>(new Date());
  const [formHours, setFormHours] = useState('');
  const [formNotes, setFormNotes] = useState('');

  // Summary stats
  const totalHours = entries.reduce((sum, e) => sum + e.hours, 0);

  // Fetch entries
  const fetchEntries = async () => {
    setLoading(true);
    try {
      // Calculate FY date range - financialYear format: "2024-2025"
      // FY 2024-2025 = July 1, 2024 to June 30, 2025
      const [startYear, endYear] = financialYear.split('-').map(Number);
      const start_date = `${startYear}-07-01`;
      const end_date = `${endYear}-06-30`;

      const response = await taxService.wfh.list({ start_date, end_date });
      setEntries(response.entries);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, [financialYear]);

  const handleOpenDialog = (entry?: WFHEntry) => {
    if (entry) {
      setEditingEntry(entry);
      setFormDate(new Date(entry.date));
      setFormHours(entry.hours.toString());
      setFormNotes(entry.notes || '');
    } else {
      setEditingEntry(null);
      setFormDate(new Date());
      setFormHours('');
      setFormNotes('');
    }
    setShowDialog(true);
  };

  const handleCloseDialog = () => {
    setShowDialog(false);
    setEditingEntry(null);
    setFormDate(new Date());
    setFormHours('');
    setFormNotes('');
  };

  const handleSubmit = async () => {
    if (!formDate || !formHours) {
      toast.error('Please fill in all required fields');
      return;
    }

    const hours = parseFloat(formHours);
    if (isNaN(hours) || hours <= 0 || hours > 24) {
      toast.error('Hours must be between 0 and 24');
      return;
    }

    setSubmitting(true);
    try {
      if (editingEntry) {
        // Update existing
        await taxService.wfh.update(editingEntry.id, {
          hours,
          notes: formNotes || undefined,
        });
        toast.success('WFH entry updated');
      } else {
        // Create new
        const data: WFHEntryCreate = {
          date: format(formDate, 'yyyy-MM-dd'),
          hours,
          notes: formNotes || undefined,
        };
        await taxService.wfh.create(data);
        toast.success('WFH entry created');
      }
      handleCloseDialog();
      fetchEntries();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteEntry) return;

    try {
      await taxService.wfh.delete(deleteEntry.id);
      toast.success('WFH entry deleted');
      setDeleteEntry(null);
      fetchEntries();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  if (loading) {
    return <PageLoader message="Loading WFH entries..." />;
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Entries</CardDescription>
            <CardTitle className="text-3xl">{entries.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Hours</CardDescription>
            <CardTitle className="text-3xl">{totalHours.toFixed(1)}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Entries Table */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Work From Home Entries</CardTitle>
              <CardDescription>FY {financialYear}</CardDescription>
            </div>
            <Button onClick={() => handleOpenDialog()}>
              <Plus className="mr-2 h-4 w-4" />
              Add Entry
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {entries.length === 0 ? (
            <EmptyState
              title="No WFH entries yet"
              description="Start tracking your work from home hours to claim ATO deductions."
              action={{
                label: 'Add First Entry',
                onClick: () => handleOpenDialog(),
              }}
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Hours</TableHead>
                  <TableHead>Notes</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {entries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>{format(new Date(entry.date), 'PPP')}</TableCell>
                    <TableCell>{entry.hours.toFixed(1)}</TableCell>
                    <TableCell className="max-w-xs truncate">{entry.notes || '-'}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleOpenDialog(entry)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setDeleteEntry(entry)}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
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

      {/* Create/Edit Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingEntry ? 'Edit' : 'Add'} WFH Entry</DialogTitle>
            <DialogDescription>
              Record hours worked from home for ATO tax deductions.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="date">Date *</Label>
              {editingEntry ? (
                <Input
                  value={format(new Date(editingEntry.date), 'PPP')}
                  disabled
                  className="bg-gray-50"
                />
              ) : (
                <DatePicker date={formDate} onDateChange={setFormDate} />
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="hours">Hours Worked *</Label>
              <Input
                id="hours"
                type="number"
                min="0.5"
                max="24"
                step="0.5"
                value={formHours}
                onChange={(e) => setFormHours(e.target.value)}
                placeholder="8.0"
              />
              <p className="text-xs text-gray-500">Between 0.5 and 24 hours</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Input
                id="notes"
                value={formNotes}
                onChange={(e) => setFormNotes(e.target.value)}
                placeholder="Optional notes"
                maxLength={1000}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCloseDialog}>
              Cancel
            </Button>
            <LoadingButton onClick={handleSubmit} loading={submitting}>
              {editingEntry ? 'Update' : 'Create'}
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      {deleteEntry && (
        <ConfirmDialog
          open={!!deleteEntry}
          onOpenChange={(open) => !open && setDeleteEntry(null)}
          onConfirm={handleDelete}
          title="Delete WFH Entry?"
          description={`Are you sure you want to delete the entry for ${format(new Date(deleteEntry.date), 'PPP')} (${deleteEntry.hours} hours)? This record must be retained for 5 years per ATO requirements. Only delete if you're certain this is outside the retention period.`}
          confirmText="Delete"
          variant="destructive"
        />
      )}
    </div>
  );
}
