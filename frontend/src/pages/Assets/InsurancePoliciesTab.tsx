import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Shield, AlertTriangle, Home, Car, Heart, User, Dog, Plane, Package, Building2, DollarSign, FileText } from 'lucide-react';
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
import type { InsurancePolicy, InsurancePolicyCreate, PolicyType, PremiumFrequency } from '@/services/assetsService';
import { getErrorMessage } from '@/lib/errorMessages';
import { toast } from 'sonner';
import { formatCurrency } from '@/lib/frequencyUtils';

export default function InsurancePoliciesTab() {
  const [policies, setPolicies] = useState<InsurancePolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState<InsurancePolicy | null>(null);
  const [deletePolicy, setDeletePolicy] = useState<InsurancePolicy | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Filter state
  const [typeFilter, setTypeFilter] = useState<string>('all');

  // Form state
  const [formType, setFormType] = useState<PolicyType>('Home');
  const [formProvider, setFormProvider] = useState('');
  const [formPolicyNumber, setFormPolicyNumber] = useState('');
  const [formCoverageAmount, setFormCoverageAmount] = useState('');
  const [formPremium, setFormPremium] = useState('');
  const [formPremiumFrequency, setFormPremiumFrequency] = useState<PremiumFrequency>('Annually');
  const [formExcess, setFormExcess] = useState('');
  const [formRenewalDate, setFormRenewalDate] = useState<Date | undefined>(undefined);
  const [formCoverageNotes, setFormCoverageNotes] = useState('');
  const [formDocumentId, setFormDocumentId] = useState<number | null>(null);

  // Fetch policies
  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (typeFilter !== 'all') {
        params.policy_type = typeFilter;
      }

      const response = await assetsService.insurance.list(params);
      setPolicies(response.policies);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, [typeFilter]);

  const resetForm = () => {
    setFormType('Home');
    setFormProvider('');
    setFormPolicyNumber('');
    setFormCoverageAmount('');
    setFormPremium('');
    setFormPremiumFrequency('Annually');
    setFormExcess('');
    setFormRenewalDate(undefined);
    setFormCoverageNotes('');
    setFormDocumentId(null);
  };

  const openAddDialog = () => {
    resetForm();
    setEditingPolicy(null);
    setShowDialog(true);
  };

  const openEditDialog = (policy: InsurancePolicy) => {
    setEditingPolicy(policy);
    setFormType(policy.policy_type);
    setFormProvider(policy.provider);
    setFormPolicyNumber(policy.policy_number || '');
    setFormCoverageAmount(policy.coverage_amount ? policy.coverage_amount.toString() : '');
    setFormPremium(policy.premium.toString());
    setFormPremiumFrequency(policy.premium_frequency);
    setFormExcess(policy.excess ? policy.excess.toString() : '');
    setFormRenewalDate(new Date(policy.renewal_date));
    setFormCoverageNotes(policy.coverage_notes || '');
    setFormDocumentId(policy.document_id ? Number(policy.document_id) : null);
    setShowDialog(true);
  };

  const handleSubmit = async () => {
    if (!formProvider || !formPremium || !formRenewalDate) {
      toast.error('Please fill in all required fields');
      return;
    }

    setSubmitting(true);
    try {
      const data: InsurancePolicyCreate = {
        policy_type: formType,
        provider: formProvider,
        policy_number: formPolicyNumber || undefined,
        coverage_amount: formCoverageAmount ? Number.parseFloat(formCoverageAmount) : undefined,
        premium: Number.parseFloat(formPremium),
        premium_frequency: formPremiumFrequency,
        excess: formExcess ? Number.parseFloat(formExcess) : undefined,
        renewal_date: format(formRenewalDate, 'yyyy-MM-dd'),
        coverage_notes: formCoverageNotes || undefined,
        document_id: formDocumentId || undefined,
      };

      if (editingPolicy) {
        await assetsService.insurance.update(editingPolicy.id, data);
        toast.success('Insurance policy updated');
      } else {
        await assetsService.insurance.create(data);
        toast.success('Insurance policy created');
      }

      setShowDialog(false);
      fetchPolicies();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deletePolicy) return;

    try {
      await assetsService.insurance.delete(deletePolicy.id);
      toast.success('Insurance policy deleted');
      setDeletePolicy(null);
      fetchPolicies();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const getPolicyIcon = (type: PolicyType) => {
    const icons = {
      'Home': Home,
      'Car': Car,
      'Health': Heart,
      'Life': User,
      'Pet': Dog,
      'Travel': Plane,
      'Contents': Package,
      'Landlord': Building2,
      'Income Protection': DollarSign,
      'Other': FileText,
    };
    const Icon = icons[type];
    return <Icon className="h-4 w-4" />;
  };

  const getPolicyBadge = (type: PolicyType) => {
    const colors = {
      'Home': 'bg-blue-100 text-blue-800',
      'Car': 'bg-green-100 text-green-800',
      'Health': 'bg-red-100 text-red-800',
      'Life': 'bg-purple-100 text-purple-800',
      'Pet': 'bg-yellow-100 text-yellow-800',
      'Travel': 'bg-cyan-100 text-cyan-800',
      'Contents': 'bg-orange-100 text-orange-800',
      'Landlord': 'bg-indigo-100 text-indigo-800',
      'Income Protection': 'bg-pink-100 text-pink-800',
      'Other': 'bg-gray-100 text-gray-800',
    };
    return (
      <Badge className={colors[type]} variant="secondary">
        <span className="flex items-center gap-1">
          {getPolicyIcon(type)}
          {type}
        </span>
      </Badge>
    );
  };

  const getRenewalBadge = (daysUntilRenewal: number) => {
    if (daysUntilRenewal < 0) {
      return <Badge variant="destructive">Expired</Badge>;
    } else if (daysUntilRenewal <= 7) {
      return <Badge variant="destructive" className="flex items-center gap-1">
        <AlertTriangle className="h-3 w-3" />
        {daysUntilRenewal} days
      </Badge>;
    } else if (daysUntilRenewal <= 30) {
      return <Badge className="bg-yellow-100 text-yellow-800 flex items-center gap-1">
        <AlertTriangle className="h-3 w-3" />
        {daysUntilRenewal} days
      </Badge>;
    } else {
      return <Badge variant="secondary">{daysUntilRenewal} days</Badge>;
    }
  };

  if (loading) {
    return <PageLoader message="Loading insurance policies..." />;
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
              Add Policy
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="w-64">
              <Label>Policy Type</Label>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="bg-white dark:bg-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="Home">🏠 Home</SelectItem>
                  <SelectItem value="Car">🚗 Car</SelectItem>
                  <SelectItem value="Health">❤️ Health</SelectItem>
                  <SelectItem value="Life">👤 Life</SelectItem>
                  <SelectItem value="Pet">🐶 Pet</SelectItem>
                  <SelectItem value="Travel">✈️ Travel</SelectItem>
                  <SelectItem value="Contents">📦 Contents</SelectItem>
                  <SelectItem value="Landlord">🏢 Landlord</SelectItem>
                  <SelectItem value="Income Protection">💰 Income Protection</SelectItem>
                  <SelectItem value="Other">📄 Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Policies
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{policies.length}</div>
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
              {policies.filter(p => p.days_until_renewal >= 0 && p.days_until_renewal <= 30).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Total Annual Premium
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {formatCurrency(
                policies.reduce((sum, p) => {
                  const annual = p.premium_frequency === 'Annually' ? p.premium : p.premium * 12;
                  return sum + annual;
                }, 0)
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Policies Table */}
      {policies.length === 0 ? (
        <EmptyState
          icon={Shield}
          title="No insurance policies"
          description="Add your first insurance policy to start tracking renewals and premiums."
          action={{
            label: 'Add Policy',
            onClick: openAddDialog
          }}
        />
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Insurance Policies</CardTitle>
            <CardDescription>
              {policies.length} {policies.length === 1 ? 'policy' : 'policies'} found
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Type</TableHead>
                    <TableHead>Provider</TableHead>
                    <TableHead>Policy Number</TableHead>
                    <TableHead className="text-right">Premium</TableHead>
                    <TableHead>Renewal Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {policies.map((policy) => (
                    <TableRow key={policy.id}>
                      <TableCell>{getPolicyBadge(policy.policy_type)}</TableCell>
                      <TableCell className="font-medium">{policy.provider}</TableCell>
                      <TableCell className="text-gray-500">
                        {policy.policy_number || '—'}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="font-medium">{formatCurrency(policy.premium)}</div>
                        <div className="text-xs text-gray-500">{policy.premium_frequency}</div>
                      </TableCell>
                      <TableCell>{format(new Date(policy.renewal_date), 'MMM dd, yyyy')}</TableCell>
                      <TableCell>{getRenewalBadge(policy.days_until_renewal)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openEditDialog(policy)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setDeletePolicy(policy)}
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

      {/* Add/Edit Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="bg-white dark:bg-white max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingPolicy ? 'Edit Insurance Policy' : 'Add Insurance Policy'}
            </DialogTitle>
            <DialogDescription>
              {editingPolicy
                ? 'Update insurance policy details'
                : 'Create a new insurance policy'}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="type">Policy Type *</Label>
                <Select value={formType} onValueChange={(value) => setFormType(value as PolicyType)}>
                  <SelectTrigger id="type" className="bg-white dark:bg-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white dark:bg-white">
                    <SelectItem value="Home">🏠 Home</SelectItem>
                    <SelectItem value="Car">🚗 Car</SelectItem>
                    <SelectItem value="Health">❤️ Health</SelectItem>
                    <SelectItem value="Life">👤 Life</SelectItem>
                    <SelectItem value="Pet">🐶 Pet</SelectItem>
                    <SelectItem value="Travel">✈️ Travel</SelectItem>
                    <SelectItem value="Contents">📦 Contents</SelectItem>
                    <SelectItem value="Landlord">🏢 Landlord</SelectItem>
                    <SelectItem value="Income Protection">💰 Income Protection</SelectItem>
                    <SelectItem value="Other">📄 Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="provider">Provider *</Label>
                <Input
                  id="provider"
                  value={formProvider}
                  onChange={(e) => setFormProvider(e.target.value)}
                  placeholder="e.g., NRMA, AAMI"
                  className="bg-white dark:bg-white"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="policyNumber">Policy Number</Label>
              <Input
                id="policyNumber"
                value={formPolicyNumber}
                onChange={(e) => setFormPolicyNumber(e.target.value)}
                placeholder="Optional"
                className="bg-white dark:bg-white"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="premium">Premium *</Label>
                <Input
                  id="premium"
                  type="number"
                  step="0.01"
                  value={formPremium}
                  onChange={(e) => setFormPremium(e.target.value)}
                  placeholder="0.00"
                  className="bg-white dark:bg-white"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="frequency">Frequency *</Label>
                <Select
                  value={formPremiumFrequency}
                  onValueChange={(value) => setFormPremiumFrequency(value as PremiumFrequency)}
                >
                  <SelectTrigger id="frequency" className="bg-white dark:bg-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white dark:bg-white">
                    <SelectItem value="Monthly">Monthly</SelectItem>
                    <SelectItem value="Annually">Annually</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="coverage">Coverage Amount</Label>
                <Input
                  id="coverage"
                  type="number"
                  step="0.01"
                  value={formCoverageAmount}
                  onChange={(e) => setFormCoverageAmount(e.target.value)}
                  placeholder="Optional"
                  className="bg-white dark:bg-white"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="excess">Excess</Label>
                <Input
                  id="excess"
                  type="number"
                  step="0.01"
                  value={formExcess}
                  onChange={(e) => setFormExcess(e.target.value)}
                  placeholder="Optional"
                  className="bg-white dark:bg-white"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Renewal Date *</Label>
              <DatePicker
                date={formRenewalDate}
                onDateChange={setFormRenewalDate}
                placeholder="Select renewal date"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Coverage Notes</Label>
              <Textarea
                id="notes"
                value={formCoverageNotes}
                onChange={(e) => setFormCoverageNotes(e.target.value)}
                placeholder="Optional notes about coverage details..."
                className="bg-white dark:bg-white"
                rows={3}
              />
            </div>

            <FileUploadInput
              category="INSURANCE"
              fileId={formDocumentId}
              onUploadSuccess={(id) => setFormDocumentId(id)}
              onDelete={() => setFormDocumentId(null)}
              label="Policy Document (optional)"
            />
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>
              Cancel
            </Button>
            <LoadingButton onClick={handleSubmit} loading={submitting}>
              {editingPolicy ? 'Update' : 'Create'}
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      {deletePolicy && (
        <ConfirmDialog
          open={!!deletePolicy}
          onOpenChange={(open) => !open && setDeletePolicy(null)}
          onConfirm={handleDelete}
          title="Delete Insurance Policy?"
          description={`Are you sure you want to delete the ${deletePolicy.policy_type} policy from ${deletePolicy.provider}? This action cannot be undone.`}
          confirmText="Delete"
          variant="destructive"
        />
      )}
    </div>
  );
}
