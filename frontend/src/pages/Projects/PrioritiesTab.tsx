import { useState, useEffect } from 'react';
import { projectsService, type PriorityItem, type PriorityStatus } from '@/services/projectsService';
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
import { Plus, Edit, Trash2, ArrowRight, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

export default function PrioritiesTab() {
  const [items, setItems] = useState<PriorityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [convertDialogOpen, setConvertDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<PriorityItem | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [formDescription, setFormDescription] = useState('');
  const [formCost, setFormCost] = useState('');
  const [formSeverity, setFormSeverity] = useState('3');
  const [formFrequency, setFormFrequency] = useState('3');
  const [formStatus, setFormStatus] = useState<PriorityStatus>('Pending');

  // Convert to project form
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [projectBudget, setProjectBudget] = useState('');

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      setLoading(true);
      const response = await projectsService.priorities.list();
      setItems(response.items);
    } catch (error) {
      console.error('Failed to load priority items:', error);
      toast.error('Failed to load priority items');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormDescription('');
    setFormCost('');
    setFormSeverity('3');
    setFormFrequency('3');
    setFormStatus('Pending');
  };

  const resetConvertForm = () => {
    setProjectName('');
    setProjectDescription('');
    setProjectBudget('');
  };

  const openAddDialog = () => {
    resetForm();
    setAddDialogOpen(true);
  };

  const openEditDialog = (item: PriorityItem) => {
    setSelectedItem(item);
    setFormDescription(item.description);
    setFormCost(item.cost.toString());
    setFormSeverity(item.severity.toString());
    setFormFrequency(item.frequency.toString());
    setFormStatus(item.status);
    setEditDialogOpen(true);
  };

  const openConvertDialog = (item: PriorityItem) => {
    setSelectedItem(item);
    setProjectName(item.description);
    setProjectDescription(item.description);
    setProjectBudget(item.cost.toString());
    setConvertDialogOpen(true);
  };

  const openDeleteDialog = (item: PriorityItem) => {
    setSelectedItem(item);
    setDeleteDialogOpen(true);
  };

  const handleAdd = async () => {
    if (!formDescription.trim() || !formCost) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      setSubmitting(true);
      await projectsService.priorities.create({
        description: formDescription.trim(),
        cost: parseFloat(formCost),
        severity: parseInt(formSeverity),
        frequency: parseInt(formFrequency),
      });
      toast.success('Priority item created');
      setAddDialogOpen(false);
      loadItems();
    } catch (error) {
      console.error('Failed to create priority item:', error);
      toast.error('Failed to create priority item');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = async () => {
    if (!selectedItem || !formDescription.trim()) {
      return;
    }

    try {
      setSubmitting(true);
      await projectsService.priorities.update(selectedItem.id, {
        description: formDescription.trim(),
        cost: formCost ? parseFloat(formCost) : undefined,
        severity: parseInt(formSeverity),
        frequency: parseInt(formFrequency),
        status: formStatus,
      });
      toast.success('Priority item updated');
      setEditDialogOpen(false);
      loadItems();
    } catch (error) {
      console.error('Failed to update priority item:', error);
      toast.error('Failed to update priority item');
    } finally {
      setSubmitting(false);
    }
  };

  const handleConvert = async () => {
    if (!selectedItem || !projectName.trim()) {
      toast.error('Please provide a project name');
      return;
    }

    try {
      setSubmitting(true);
      await projectsService.priorities.convertToProject(selectedItem.id, {
        project_name: projectName.trim(),
        description: projectDescription.trim() || undefined,
        budget: projectBudget ? parseFloat(projectBudget) : undefined,
      });
      toast.success('Converted to project successfully');
      setConvertDialogOpen(false);
      resetConvertForm();
      loadItems();
    } catch (error) {
      console.error('Failed to convert to project:', error);
      toast.error('Failed to convert to project');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedItem) return;

    try {
      setSubmitting(true);
      await projectsService.priorities.delete(selectedItem.id);
      toast.success('Priority item deleted');
      setDeleteDialogOpen(false);
      loadItems();
    } catch (error) {
      console.error('Failed to delete priority item:', error);
      toast.error('Failed to delete priority item');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status: PriorityStatus) => {
    const variants: Record<PriorityStatus, { variant: any; label: string }> = {
      Pending: { variant: 'secondary', label: 'Pending' },
      ConvertedToProject: { variant: 'default', label: 'Converted' },
      Done: { variant: 'default', label: 'Done' },
      Dismissed: { variant: 'outline', label: 'Dismissed' },
    };
    const config = variants[status];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getNetScoreBadge = (score: number) => {
    if (score >= 5) {
      return <Badge className="bg-green-100 text-green-800">High Priority ({score})</Badge>;
    } else if (score >= 2) {
      return <Badge className="bg-yellow-100 text-yellow-800">Medium ({score})</Badge>;
    } else {
      return <Badge variant="outline">Low ({score})</Badge>;
    }
  };

  // Calculate summary stats
  const pendingItems = items.filter(i => i.status === 'Pending');
  const highPriorityItems = pendingItems.filter(i => i.net_score >= 5);

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
              Total Items
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{items.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              Pending
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pendingItems.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              High Priority
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center gap-2">
              {highPriorityItems.length}
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Items Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Priority Items</CardTitle>
            <Button onClick={openAddDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Add Item
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {items.length === 0 ? (
            <EmptyState
              title="No priority items"
              description="Add your first repair or improvement to prioritize."
              action={{ label: 'Add Item', onClick: openAddDialog }}
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Description</TableHead>
                  <TableHead className="text-right">Cost</TableHead>
                  <TableHead className="text-center">Severity</TableHead>
                  <TableHead className="text-center">Frequency</TableHead>
                  <TableHead className="text-center">Net Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-medium max-w-md">
                      {item.description}
                    </TableCell>
                    <TableCell className="text-right">
                      ${item.cost.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </TableCell>
                    <TableCell className="text-center">
                      <Badge variant="outline">{item.severity}</Badge>
                    </TableCell>
                    <TableCell className="text-center">
                      <Badge variant="outline">{item.frequency}</Badge>
                    </TableCell>
                    <TableCell className="text-center">
                      {getNetScoreBadge(item.net_score)}
                    </TableCell>
                    <TableCell>{getStatusBadge(item.status)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        {item.status === 'Pending' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openConvertDialog(item)}
                            title="Convert to Project"
                          >
                            <ArrowRight className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openEditDialog(item)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openDeleteDialog(item)}
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
        <DialogContent className="bg-white dark:bg-white">
          <DialogHeader>
            <DialogTitle>Add Priority Item</DialogTitle>
            <DialogDescription>
              Add a repair or improvement item to prioritize. Scores are calculated automatically.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="description">Description *</Label>
              <Input
                id="description"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                placeholder="e.g., Fix leaking roof"
              />
            </div>
            <div>
              <Label htmlFor="cost">Estimated Cost (AUD) *</Label>
              <Input
                id="cost"
                type="number"
                step="0.01"
                min="0"
                value={formCost}
                onChange={(e) => setFormCost(e.target.value)}
                placeholder="0.00"
              />
            </div>
            <div>
              <Label htmlFor="severity">Severity (1-5) *</Label>
              <Select value={formSeverity} onValueChange={setFormSeverity}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="1">1 - Cosmetic (No functional impact)</SelectItem>
                  <SelectItem value="2">2 - Minor (Small inconvenience)</SelectItem>
                  <SelectItem value="3">3 - Moderate (Noticeable impact on daily life)</SelectItem>
                  <SelectItem value="4">4 - Significant (Major inconvenience or safety concern)</SelectItem>
                  <SelectItem value="5">5 - Critical (Urgent safety hazard or major damage)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="frequency">Frequency (1-5) *</Label>
              <Select value={formFrequency} onValueChange={setFormFrequency}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="1">1 - Rarely (Happens once a year or less)</SelectItem>
                  <SelectItem value="2">2 - Occasionally (Few times per year)</SelectItem>
                  <SelectItem value="3">3 - Regularly (Monthly or weekly)</SelectItem>
                  <SelectItem value="4">4 - Frequently (Multiple times per week)</SelectItem>
                  <SelectItem value="5">5 - Constantly (Daily or continuous issue)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddDialogOpen(false)}>
              Cancel
            </Button>
            <LoadingButton onClick={handleAdd} loading={submitting}>
              Add Item
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="bg-white dark:bg-white">
          <DialogHeader>
            <DialogTitle>Edit Priority Item</DialogTitle>
            <DialogDescription>
              Update item details. Scores will be recalculated automatically.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-description">Description *</Label>
              <Input
                id="edit-description"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="edit-cost">Estimated Cost (AUD)</Label>
              <Input
                id="edit-cost"
                type="number"
                step="0.01"
                min="0"
                value={formCost}
                onChange={(e) => setFormCost(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="edit-severity">Severity (1-5)</Label>
              <Select value={formSeverity} onValueChange={setFormSeverity}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="1">1 - Cosmetic (No functional impact)</SelectItem>
                  <SelectItem value="2">2 - Minor (Small inconvenience)</SelectItem>
                  <SelectItem value="3">3 - Moderate (Noticeable impact on daily life)</SelectItem>
                  <SelectItem value="4">4 - Significant (Major inconvenience or safety concern)</SelectItem>
                  <SelectItem value="5">5 - Critical (Urgent safety hazard or major damage)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="edit-frequency">Frequency (1-5)</Label>
              <Select value={formFrequency} onValueChange={setFormFrequency}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="1">1 - Rarely (Happens once a year or less)</SelectItem>
                  <SelectItem value="2">2 - Occasionally (Few times per year)</SelectItem>
                  <SelectItem value="3">3 - Regularly (Monthly or weekly)</SelectItem>
                  <SelectItem value="4">4 - Frequently (Multiple times per week)</SelectItem>
                  <SelectItem value="5">5 - Constantly (Daily or continuous issue)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="edit-status">Status</Label>
              <Select value={formStatus} onValueChange={(val) => setFormStatus(val as PriorityStatus)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="Pending">Pending</SelectItem>
                  <SelectItem value="Done">Done</SelectItem>
                  <SelectItem value="Dismissed">Dismissed</SelectItem>
                </SelectContent>
              </Select>
            </div>
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

      {/* Convert to Project Dialog */}
      <Dialog open={convertDialogOpen} onOpenChange={setConvertDialogOpen}>
        <DialogContent className="bg-white dark:bg-white">
          <DialogHeader>
            <DialogTitle>Convert to Project</DialogTitle>
            <DialogDescription>
              Create a new project from this priority item. The item will be marked as converted.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="project-name">Project Name *</Label>
              <Input
                id="project-name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="e.g., Roof Repair Project"
              />
            </div>
            <div>
              <Label htmlFor="project-description">Description</Label>
              <Input
                id="project-description"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                placeholder="Project details"
              />
            </div>
            <div>
              <Label htmlFor="project-budget">Budget (AUD)</Label>
              <Input
                id="project-budget"
                type="number"
                step="0.01"
                min="0"
                value={projectBudget}
                onChange={(e) => setProjectBudget(e.target.value)}
                placeholder="0.00"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConvertDialogOpen(false)}>
              Cancel
            </Button>
            <LoadingButton onClick={handleConvert} loading={submitting}>
              Convert to Project
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="bg-white dark:bg-white">
          <DialogHeader>
            <DialogTitle>Delete Priority Item</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this item? This action cannot be undone.
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
    </div>
  );
}
