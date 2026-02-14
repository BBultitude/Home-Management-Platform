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
import type { TravelEntry, TravelEntryCreate } from '@/services/taxService';
import { getErrorMessage } from '@/lib/errorMessages';
import { toast } from 'sonner';

interface TravelTabProps {
  financialYear: string;
}

export function TravelTab({ financialYear }: TravelTabProps) {
  const [entries, setEntries] = useState<TravelEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingEntry, setEditingEntry] = useState<TravelEntry | null>(null);
  const [deleteEntry, setDeleteEntry] = useState<TravelEntry | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [formDate, setFormDate] = useState<Date | undefined>(new Date());
  const [formPurpose, setFormPurpose] = useState('');
  const [formStartLocation, setFormStartLocation] = useState('');
  const [formEndLocation, setFormEndLocation] = useState('');
  const [formDistanceKm, setFormDistanceKm] = useState('');
  const [formNotes, setFormNotes] = useState('');

  // Summary stats
  const totalTrips = entries.length;
  const totalKm = entries.reduce((sum, e) => sum + e.distance_km, 0);
  const totalDeduction = entries.reduce((sum, e) => sum + (e.deduction_amount || 0), 0);

  // Fetch entries
  const fetchEntries = async () => {
    setLoading(true);
    try {
      const [startYear] = financialYear.split('-').map(Number);
      const start_date = `${startYear}-07-01`;
      const end_date = `${startYear + 1}-06-30`;

      const response = await taxService.travel.list({ start_date, end_date });
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

  const handleOpenDialog = (entry?: TravelEntry) => {
    if (entry) {
      setEditingEntry(entry);
      setFormDate(new Date(entry.date));
      setFormPurpose(entry.purpose);
      setFormStartLocation(entry.start_location);
      setFormEndLocation(entry.end_location);
      setFormDistanceKm(entry.distance_km.toString());
      setFormNotes(entry.notes || '');
    } else {
      setEditingEntry(null);
      setFormDate(new Date());
      setFormPurpose('');
      setFormStartLocation('');
      setFormEndLocation('');
      setFormDistanceKm('');
      setFormNotes('');
    }
    setShowDialog(true);
  };

  const handleCloseDialog = () => {
    setShowDialog(false);
    setEditingEntry(null);
    setFormDate(new Date());
    setFormPurpose('');
    setFormStartLocation('');
    setFormEndLocation('');
    setFormDistanceKm('');
    setFormNotes('');
  };

  const handleSubmit = async () => {
    if (!formDate || !formPurpose || !formStartLocation || !formEndLocation || !formDistanceKm) {
      toast.error('Please fill in all required fields');
      return;
    }

    const distance = parseFloat(formDistanceKm);
    if (isNaN(distance) || distance <= 0 || distance > 10000) {
      toast.error('Distance must be between 0 and 10,000 km');
      return;
    }

    setSubmitting(true);
    try {
      if (editingEntry) {
        // Update existing
        await taxService.travel.update(editingEntry.id, {
          purpose: formPurpose,
          start_location: formStartLocation,
          end_location: formEndLocation,
          distance_km: distance,
          notes: formNotes || undefined,
        });
        toast.success('Travel entry updated');
      } else {
        // Create new
        const data: TravelEntryCreate = {
          date: format(formDate, 'yyyy-MM-dd'),
          purpose: formPurpose,
          start_location: formStartLocation,
          end_location: formEndLocation,
          distance_km: distance,
          notes: formNotes || undefined,
        };
        await taxService.travel.create(data);
        toast.success('Travel entry created');
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
      await taxService.travel.delete(deleteEntry.id);
      toast.success('Travel entry deleted');
      setDeleteEntry(null);
      fetchEntries();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  if (loading) {
    return <PageLoader message="Loading travel entries..." />;
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Trips</CardDescription>
            <CardTitle className="text-3xl">{totalTrips}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Distance</CardDescription>
            <CardTitle className="text-3xl">{totalKm.toFixed(1)} km</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Deduction</CardDescription>
            <CardTitle className="text-3xl">${totalDeduction.toFixed(2)}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Entries Table */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Work Travel Entries</CardTitle>
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
              title="No travel entries yet"
              description="Start tracking work-related travel to claim ATO deductions."
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
                  <TableHead>From → To</TableHead>
                  <TableHead>Purpose</TableHead>
                  <TableHead>Distance</TableHead>
                  <TableHead>Deduction</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {entries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>{format(new Date(entry.date), 'PP')}</TableCell>
                    <TableCell>
                      <div className="max-w-xs">
                        <div className="font-medium truncate">{entry.start_location}</div>
                        <div className="text-sm text-gray-500 truncate">→ {entry.end_location}</div>
                      </div>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">{entry.purpose}</TableCell>
                    <TableCell>{entry.distance_km.toFixed(1)} km</TableCell>
                    <TableCell>${(entry.deduction_amount || 0).toFixed(2)}</TableCell>
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
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingEntry ? 'Edit' : 'Add'} Travel Entry</DialogTitle>
            <DialogDescription>
              Record work-related travel for ATO tax deductions.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
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
                <Label htmlFor="distance">Distance (km) *</Label>
                <Input
                  id="distance"
                  type="number"
                  min="0.1"
                  max="10000"
                  step="0.1"
                  value={formDistanceKm}
                  onChange={(e) => setFormDistanceKm(e.target.value)}
                  placeholder="50.0"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="purpose">Purpose *</Label>
              <Input
                id="purpose"
                value={formPurpose}
                onChange={(e) => setFormPurpose(e.target.value)}
                placeholder="Client meeting, site visit, etc."
                maxLength={255}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="startLocation">From Location *</Label>
                <Input
                  id="startLocation"
                  value={formStartLocation}
                  onChange={(e) => setFormStartLocation(e.target.value)}
                  placeholder="Office address"
                  maxLength={255}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="endLocation">To Location *</Label>
                <Input
                  id="endLocation"
                  value={formEndLocation}
                  onChange={(e) => setFormEndLocation(e.target.value)}
                  placeholder="Client address"
                  maxLength={255}
                />
              </div>
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
          title="Delete Travel Entry?"
          description={`Are you sure you want to delete the trip from ${deleteEntry.start_location} to ${deleteEntry.end_location} on ${format(new Date(deleteEntry.date), 'PPP')}? This record must be retained for 5 years per ATO requirements. Only delete if you're certain this is outside the retention period.`}
          confirmText="Delete"
          variant="destructive"
        />
      )}
    </div>
  );
}
