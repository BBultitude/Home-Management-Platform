import { useState, useEffect } from 'react';
import { projectsService, type Project, type ProjectStatus } from '@/services/projectsService';
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
import { Plus, Edit, Trash2, CheckCircle2, Circle } from 'lucide-react';
import { toast } from 'sonner';
import { format, parseISO } from 'date-fns';

export default function ProjectsTab() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [formProjectName, setFormProjectName] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formStatus, setFormStatus] = useState<ProjectStatus>('Planned');
  const [formStartDate, setFormStartDate] = useState<Date | undefined>(undefined);
  const [formCompletionDate, setFormCompletionDate] = useState<Date | undefined>(undefined);
  const [formBudget, setFormBudget] = useState('');
  const [formActualCost, setFormActualCost] = useState('');
  const [formNotes, setFormNotes] = useState('');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await projectsService.projects.list();
      setProjects(response.projects);
    } catch (error) {
      console.error('Failed to load projects:', error);
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormProjectName('');
    setFormDescription('');
    setFormStatus('Planned');
    setFormStartDate(undefined);
    setFormCompletionDate(undefined);
    setFormBudget('');
    setFormActualCost('');
    setFormNotes('');
  };

  const openAddDialog = () => {
    resetForm();
    setAddDialogOpen(true);
  };

  const openEditDialog = (project: Project) => {
    setSelectedProject(project);
    setFormProjectName(project.project_name);
    setFormDescription(project.description || '');
    setFormStatus(project.status);
    setFormStartDate(project.start_date ? parseISO(project.start_date) : undefined);
    setFormCompletionDate(project.completion_date ? parseISO(project.completion_date) : undefined);
    setFormBudget(project.budget?.toString() || '');
    setFormActualCost(project.actual_cost?.toString() || '');
    setFormNotes(project.notes || '');
    setEditDialogOpen(true);
  };

  const openDeleteDialog = (project: Project) => {
    setSelectedProject(project);
    setDeleteDialogOpen(true);
  };

  const handleAdd = async () => {
    if (!formProjectName.trim()) {
      toast.error('Please provide a project name');
      return;
    }

    try {
      setSubmitting(true);
      await projectsService.projects.create({
        project_name: formProjectName.trim(),
        description: formDescription.trim() || undefined,
        status: formStatus,
        start_date: formStartDate ? format(formStartDate, 'yyyy-MM-dd') : undefined,
        completion_date: formCompletionDate ? format(formCompletionDate, 'yyyy-MM-dd') : undefined,
        budget: formBudget ? parseFloat(formBudget) : undefined,
        actual_cost: formActualCost ? parseFloat(formActualCost) : undefined,
        notes: formNotes.trim() || undefined,
      });
      toast.success('Project created');
      setAddDialogOpen(false);
      loadProjects();
    } catch (error) {
      console.error('Failed to create project:', error);
      toast.error('Failed to create project');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = async () => {
    if (!selectedProject || !formProjectName.trim()) {
      return;
    }

    try {
      setSubmitting(true);
      await projectsService.projects.update(selectedProject.id, {
        project_name: formProjectName.trim(),
        description: formDescription.trim() || undefined,
        status: formStatus,
        start_date: formStartDate ? format(formStartDate, 'yyyy-MM-dd') : undefined,
        completion_date: formCompletionDate ? format(formCompletionDate, 'yyyy-MM-dd') : undefined,
        budget: formBudget ? parseFloat(formBudget) : undefined,
        actual_cost: formActualCost ? parseFloat(formActualCost) : undefined,
        notes: formNotes.trim() || undefined,
      });
      toast.success('Project updated');
      setEditDialogOpen(false);
      loadProjects();
    } catch (error) {
      console.error('Failed to update project:', error);
      toast.error('Failed to update project');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedProject) return;

    try {
      setSubmitting(true);
      await projectsService.projects.delete(selectedProject.id);
      toast.success('Project deleted');
      setDeleteDialogOpen(false);
      loadProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
      toast.error('Failed to delete project');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status: ProjectStatus) => {
    const variants: Record<ProjectStatus, { variant: any; label: string; icon?: any }> = {
      Planned: { variant: 'secondary', label: 'Planned', icon: Circle },
      Approved: { variant: 'default', label: 'Approved', icon: CheckCircle2 },
      InProgress: { variant: 'default', label: 'In Progress', icon: Circle },
      Completed: { variant: 'default', label: 'Completed', icon: CheckCircle2 },
      Cancelled: { variant: 'outline', label: 'Cancelled', icon: Circle },
    };
    const config = variants[status];
    const Icon = config.icon;
    return (
      <Badge variant={config.variant} className="flex items-center gap-1 w-fit">
        {Icon && <Icon className="h-3 w-3" />}
        {config.label}
      </Badge>
    );
  };

  // Calculate summary stats
  const activeProjects = projects.filter(p =>
    p.status === 'Approved' || p.status === 'InProgress'
  );
  const completedProjects = projects.filter(p => p.status === 'Completed');
  const totalBudget = projects
    .filter(p => p.budget && p.status !== 'Cancelled')
    .reduce((sum, p) => sum + (p.budget || 0), 0);

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
              Active Projects
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeProjects.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              Completed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completedProjects.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Budget
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${totalBudget.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Projects Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Projects</CardTitle>
            <Button onClick={openAddDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Add Project
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {projects.length === 0 ? (
            <EmptyState
              title="No projects"
              description="Create your first home improvement project."
              action={{ label: 'Add Project', onClick: openAddDialog }}
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Project Name</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Start Date</TableHead>
                  <TableHead>Completion Date</TableHead>
                  <TableHead className="text-right">Budget</TableHead>
                  <TableHead className="text-right">Actual Cost</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projects.map((project) => (
                  <TableRow key={project.id}>
                    <TableCell className="font-medium max-w-xs">
                      <div>
                        <div>{project.project_name}</div>
                        {project.description && (
                          <div className="text-sm text-gray-500 truncate">
                            {project.description}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(project.status)}</TableCell>
                    <TableCell>
                      {project.start_date
                        ? format(parseISO(project.start_date), 'dd MMM yyyy')
                        : '-'}
                    </TableCell>
                    <TableCell>
                      {project.completion_date
                        ? format(parseISO(project.completion_date), 'dd MMM yyyy')
                        : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      {project.budget
                        ? `$${project.budget.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                        : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      {project.actual_cost
                        ? `$${project.actual_cost.toLocaleString('en-AU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                        : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openEditDialog(project)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openDeleteDialog(project)}
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
            <DialogTitle>Add Project</DialogTitle>
            <DialogDescription>
              Create a new home improvement project.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="project-name">Project Name *</Label>
              <Input
                id="project-name"
                value={formProjectName}
                onChange={(e) => setFormProjectName(e.target.value)}
                placeholder="e.g., Kitchen Renovation"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                placeholder="Project details and scope"
                rows={3}
              />
            </div>
            <div>
              <Label htmlFor="status">Status</Label>
              <Select value={formStatus} onValueChange={(val) => setFormStatus(val as ProjectStatus)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="Planned">Planned</SelectItem>
                  <SelectItem value="Approved">Approved</SelectItem>
                  <SelectItem value="InProgress">In Progress</SelectItem>
                  <SelectItem value="Completed">Completed</SelectItem>
                  <SelectItem value="Cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Start Date</Label>
                <DatePicker
                  date={formStartDate}
                  onDateChange={setFormStartDate}
                  placeholder="Select start date"
                />
              </div>
              <div>
                <Label>Completion Date</Label>
                <DatePicker
                  date={formCompletionDate}
                  onDateChange={setFormCompletionDate}
                  placeholder="Select completion date"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="budget">Budget (AUD)</Label>
                <Input
                  id="budget"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formBudget}
                  onChange={(e) => setFormBudget(e.target.value)}
                  placeholder="0.00"
                />
              </div>
              <div>
                <Label htmlFor="actual-cost">Actual Cost (AUD)</Label>
                <Input
                  id="actual-cost"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formActualCost}
                  onChange={(e) => setFormActualCost(e.target.value)}
                  placeholder="0.00"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={formNotes}
                onChange={(e) => setFormNotes(e.target.value)}
                placeholder="Additional notes"
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddDialogOpen(false)}>
              Cancel
            </Button>
            <LoadingButton onClick={handleAdd} loading={submitting}>
              Add Project
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="bg-white dark:bg-white max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Project</DialogTitle>
            <DialogDescription>
              Update project details.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-project-name">Project Name *</Label>
              <Input
                id="edit-project-name"
                value={formProjectName}
                onChange={(e) => setFormProjectName(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                rows={3}
              />
            </div>
            <div>
              <Label htmlFor="edit-status">Status</Label>
              <Select value={formStatus} onValueChange={(val) => setFormStatus(val as ProjectStatus)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="Planned">Planned</SelectItem>
                  <SelectItem value="Approved">Approved</SelectItem>
                  <SelectItem value="InProgress">In Progress</SelectItem>
                  <SelectItem value="Completed">Completed</SelectItem>
                  <SelectItem value="Cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Start Date</Label>
                <DatePicker
                  date={formStartDate}
                  onDateChange={setFormStartDate}
                  placeholder="Select start date"
                />
              </div>
              <div>
                <Label>Completion Date</Label>
                <DatePicker
                  date={formCompletionDate}
                  onDateChange={setFormCompletionDate}
                  placeholder="Select completion date"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-budget">Budget (AUD)</Label>
                <Input
                  id="edit-budget"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formBudget}
                  onChange={(e) => setFormBudget(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="edit-actual-cost">Actual Cost (AUD)</Label>
                <Input
                  id="edit-actual-cost"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formActualCost}
                  onChange={(e) => setFormActualCost(e.target.value)}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="edit-notes">Notes</Label>
              <Textarea
                id="edit-notes"
                value={formNotes}
                onChange={(e) => setFormNotes(e.target.value)}
                rows={3}
              />
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

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="bg-white dark:bg-white">
          <DialogHeader>
            <DialogTitle>Delete Project</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{selectedProject?.project_name}"?
              This will also delete all associated quotes. This action cannot be undone.
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
