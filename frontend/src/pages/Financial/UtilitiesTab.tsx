import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Zap, Flame, Droplet, Home } from 'lucide-react';
import { format, differenceInDays } from 'date-fns';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { EmptyState } from '@/components/common/EmptyState';
import { PageLoader } from '@/components/common/PageLoader';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { LoadingButton } from '@/components/ui/loading-button';
import { DatePicker } from '@/components/forms/DatePicker';
import { financialService } from '@/services/financialService';
import type { Utility, UtilityCreate, UtilityType, UtilityStatsResponse } from '@/services/financialService';
import { getErrorMessage } from '@/lib/errorMessages';
import { toast } from 'sonner';
import { formatCurrency } from '@/lib/frequencyUtils';
import UtilityGraphs from './UtilityGraphs';

export function UtilitiesTab() {
  const [utilities, setUtilities] = useState<Utility[]>([]);
  const [stats, setStats] = useState<UtilityStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingUtility, setEditingUtility] = useState<Utility | null>(null);
  const [deleteUtility, setDeleteUtility] = useState<Utility | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Filter state
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [startDateFilter, setStartDateFilter] = useState<Date | undefined>(undefined);
  const [endDateFilter, setEndDateFilter] = useState<Date | undefined>(undefined);

  // Form state
  const [formType, setFormType] = useState<UtilityType>('electricity');
  const [formProvider, setFormProvider] = useState('');
  const [formPeriodStart, setFormPeriodStart] = useState<Date | undefined>(undefined);
  const [formPeriodEnd, setFormPeriodEnd] = useState<Date | undefined>(undefined);
  const [formUsage, setFormUsage] = useState('');
  const [formUnit, setFormUnit] = useState('');
  const [formCost, setFormCost] = useState('');
  const [formSolarFeedIn, setFormSolarFeedIn] = useState('');
  const [formSolarFeedInCredit, setFormSolarFeedInCredit] = useState('');
  const [formNotes, setFormNotes] = useState('');

  // Fetch utilities
  const fetchUtilities = async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (typeFilter !== 'all') {
        params.utility_type = typeFilter;
      }
      if (startDateFilter) {
        params.start_date = format(startDateFilter, 'yyyy-MM-dd');
      }
      if (endDateFilter) {
        params.end_date = format(endDateFilter, 'yyyy-MM-dd');
      }

      const response = await financialService.utilities.list(params);
      setUtilities(response.utilities);

      // Fetch stats if type filter is set
      if (typeFilter !== 'all') {
        const statsParams: Record<string, string> = {};
        if (startDateFilter) statsParams.start_date = format(startDateFilter, 'yyyy-MM-dd');
        if (endDateFilter) statsParams.end_date = format(endDateFilter, 'yyyy-MM-dd');
        const statsResp = await financialService.utilities.stats(typeFilter as UtilityType, statsParams);
        setStats(statsResp);
      } else {
        setStats(null);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUtilities();
  }, [typeFilter, startDateFilter, endDateFilter]);

  const resetForm = () => {
    setFormType('electricity');
    setFormProvider('');
    setFormPeriodStart(undefined);
    setFormPeriodEnd(undefined);
    setFormUsage('');
    setFormUnit('kWh');
    setFormCost('');
    setFormSolarFeedIn('');
    setFormSolarFeedInCredit('');
    setFormNotes('');
  };

  const handleOpenDialog = (utility?: Utility) => {
    if (utility) {
      setEditingUtility(utility);
      setFormType(utility.utility_type);
      setFormProvider(utility.provider);
      setFormPeriodStart(new Date(utility.billing_period_start));
      setFormPeriodEnd(new Date(utility.billing_period_end));
      setFormUsage(utility.usage !== null && utility.usage !== undefined ? utility.usage.toString() : '');
      setFormUnit(utility.unit || '');
      setFormCost(utility.cost.toString());
      setFormSolarFeedIn(utility.solar_feed_in !== null && utility.solar_feed_in !== undefined ? utility.solar_feed_in.toString() : '');
      setFormSolarFeedInCredit(utility.solar_feed_in_credit !== null && utility.solar_feed_in_credit !== undefined ? utility.solar_feed_in_credit.toString() : '');
      setFormNotes(utility.notes || '');
    } else {
      setEditingUtility(null);
      resetForm();
    }
    setShowDialog(true);
  };

  const handleCloseDialog = () => {
    setShowDialog(false);
    setEditingUtility(null);
    resetForm();
  };

  type ParsedFormValues = {
    cost: number;
    usage: number | null;
    solarFeedIn: number | null;
    solarFeedInCredit: number | null;
  };

  const validateAndParseForm = (): { error: string } | { values: ParsedFormValues } => {
    const isFixedCost = formType === 'rates';

    if (!formProvider || !formPeriodStart || !formPeriodEnd || !formCost) {
      return { error: 'Please fill in all required fields' };
    }
    if (!isFixedCost && (!formUsage || !formUnit)) {
      return { error: 'Please enter usage and unit for metered utilities' };
    }
    if (formPeriodStart >= formPeriodEnd) {
      return { error: 'End date must be after start date' };
    }

    const cost = Number.parseFloat(formCost);
    if (Number.isNaN(cost) || cost <= 0) {
      return { error: 'Cost must be greater than 0' };
    }

    const usage = formUsage ? Number.parseFloat(formUsage) : null;
    if (usage !== null && (Number.isNaN(usage) || usage <= 0)) {
      return { error: 'Usage must be greater than 0' };
    }

    const solarFeedIn = formSolarFeedIn ? Number.parseFloat(formSolarFeedIn) : null;
    if (solarFeedIn !== null && (Number.isNaN(solarFeedIn) || solarFeedIn < 0)) {
      return { error: 'Solar feed-in must be 0 or greater' };
    }

    const solarFeedInCredit = formSolarFeedInCredit ? Number.parseFloat(formSolarFeedInCredit) : null;
    if (solarFeedInCredit !== null && (Number.isNaN(solarFeedInCredit) || solarFeedInCredit < 0)) {
      return { error: 'Solar feed-in credit must be 0 or greater' };
    }

    return { values: { cost, usage, solarFeedIn, solarFeedInCredit } };
  };

  const handleSubmit = async () => {
    const result = validateAndParseForm();
    if ('error' in result) {
      toast.error(result.error);
      return;
    }

    const { cost, usage, solarFeedIn, solarFeedInCredit } = result.values;
    // formPeriodStart and formPeriodEnd are guaranteed non-null after validation
    const periodStart = formPeriodStart!;
    const periodEnd = formPeriodEnd!;

    const payload = {
      utility_type: formType,
      provider: formProvider,
      billing_period_start: format(periodStart, 'yyyy-MM-dd'),
      billing_period_end: format(periodEnd, 'yyyy-MM-dd'),
      usage,
      unit: formUnit || null,
      cost,
      solar_feed_in: formType === 'electricity' ? solarFeedIn : null,
      solar_feed_in_credit: formType === 'electricity' ? solarFeedInCredit : null,
      notes: formNotes || undefined,
    };

    setSubmitting(true);
    try {
      if (editingUtility) {
        await financialService.utilities.update(editingUtility.id, payload);
        toast.success('Utility entry updated');
      } else {
        await financialService.utilities.create(payload as UtilityCreate);
        toast.success('Utility entry created');
      }
      handleCloseDialog();
      fetchUtilities();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteUtility) return;

    try {
      await financialService.utilities.delete(deleteUtility.id);
      toast.success('Utility entry deleted');
      setDeleteUtility(null);
      fetchUtilities();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const getBillingDays = (start: string, end: string): number => {
    return differenceInDays(new Date(end), new Date(start)) + 1;
  };

  const getUtilityIcon = (type: UtilityType) => {
    const icons = {
      electricity: Zap,
      gas: Flame,
      water: Droplet,
      rates: Home,
    };
    const Icon = icons[type];
    return <Icon className="h-4 w-4" />;
  };

  const getUtilityBadge = (type: UtilityType) => {
    const colors = {
      electricity: 'bg-yellow-100 text-yellow-800',
      gas: 'bg-orange-100 text-orange-800',
      water: 'bg-blue-100 text-blue-800',
      rates: 'bg-gray-100 text-gray-800',
    };
    return (
      <Badge className={colors[type]} variant="secondary">
        <span className="flex items-center gap-1">
          {getUtilityIcon(type)}
          {type.charAt(0).toUpperCase() + type.slice(1)}
        </span>
      </Badge>
    );
  };

  if (loading) {
    return <PageLoader message="Loading utilities..." />;
  }

  return (
    <Tabs defaultValue="data" className="space-y-6">
      <TabsList className="grid w-full max-w-md grid-cols-2">
        <TabsTrigger value="data">Data Entry</TabsTrigger>
        <TabsTrigger value="graphs">Graphs & Analytics</TabsTrigger>
      </TabsList>

      <TabsContent value="data" className="space-y-6">
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Utility Type</Label>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="electricity">⚡ Electricity</SelectItem>
                  <SelectItem value="gas">🔥 Gas</SelectItem>
                  <SelectItem value="water">💧 Water</SelectItem>
                  <SelectItem value="rates">🏠 Rates</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Start Date</Label>
              <DatePicker date={startDateFilter} onDateChange={setStartDateFilter} />
            </div>

            <div className="space-y-2">
              <Label>End Date</Label>
              <DatePicker date={endDateFilter} onDateChange={setEndDateFilter} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards (shown when type filter is active) */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Average Cost</CardDescription>
              <CardTitle className="text-3xl">{formatCurrency(stats.average_cost)}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Total Usage</CardDescription>
              <CardTitle className="text-3xl">{stats.total_usage.toFixed(2)}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Avg Cost/Unit</CardDescription>
              <CardTitle className="text-3xl">
                {stats.total_usage > 0 ? formatCurrency(stats.total_cost / stats.total_usage) : '$0.00'}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>
      )}

      {/* Utilities Table */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Utility Entries</CardTitle>
              <CardDescription>{utilities.length} entries</CardDescription>
            </div>
            <Button onClick={() => handleOpenDialog()}>
              <Plus className="mr-2 h-4 w-4" />
              Add Entry
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {utilities.length === 0 ? (
            <EmptyState
              title="No utility entries yet"
              description="Track your utility costs and usage patterns."
              action={{
                label: 'Add First Entry',
                onClick: () => handleOpenDialog(),
              }}
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Provider</TableHead>
                  <TableHead>Period</TableHead>
                  <TableHead>Days</TableHead>
                  <TableHead>Usage</TableHead>
                  <TableHead>Avg Daily</TableHead>
                  <TableHead>Cost</TableHead>
                  <TableHead>Cost/Unit</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {utilities.map((utility) => {
                  const days = getBillingDays(utility.billing_period_start, utility.billing_period_end);
                  return (
                    <TableRow key={utility.id}>
                      <TableCell>{getUtilityBadge(utility.utility_type)}</TableCell>
                      <TableCell>{utility.provider}</TableCell>
                      <TableCell className="text-sm">
                        {format(new Date(utility.billing_period_start), 'MMM d')} -{' '}
                        {format(new Date(utility.billing_period_end), 'MMM d, yyyy')}
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">{days}d</span>
                      </TableCell>
                      <TableCell>
                        {utility.usage !== null && utility.usage !== undefined
                          ? `${utility.usage.toFixed(2)} ${utility.unit ?? ''}`
                          : <span className="text-muted-foreground text-sm">—</span>
                        }
                      </TableCell>
                      <TableCell>
                        {utility.usage !== null && utility.usage !== undefined && days > 0
                          ? <span className="text-sm">{(utility.usage / days).toFixed(2)} {utility.unit ?? ''}/day</span>
                          : <span className="text-muted-foreground text-sm">—</span>
                        }
                      </TableCell>
                      <TableCell>
                        <div>
                          {formatCurrency(utility.cost)}
                          {utility.solar_feed_in_credit !== null && utility.solar_feed_in_credit !== undefined && utility.solar_feed_in_credit > 0 && (
                            <div className="text-xs text-green-600">
                              -{formatCurrency(utility.solar_feed_in_credit)} solar
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        {utility.cost_per_unit !== null && utility.cost_per_unit !== undefined
                          ? formatCurrency(utility.cost_per_unit)
                          : <span className="text-muted-foreground text-sm">—</span>
                        }
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleOpenDialog(utility)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setDeleteUtility(utility)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Create/Edit Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingUtility ? 'Edit' : 'Add'} Utility Entry</DialogTitle>
            <DialogDescription>
              Track utility costs and usage.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="type">Utility Type *</Label>
                <Select value={formType} onValueChange={(value) => setFormType(value as UtilityType)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="electricity">⚡ Electricity</SelectItem>
                    <SelectItem value="gas">🔥 Gas</SelectItem>
                    <SelectItem value="water">💧 Water</SelectItem>
                    <SelectItem value="rates">🏠 Rates</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="provider">Provider *</Label>
                <Input
                  id="provider"
                  value={formProvider}
                  onChange={(e) => setFormProvider(e.target.value)}
                  placeholder="AGL, Origin, etc."
                  maxLength={255}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Billing Period Start *</Label>
                <DatePicker date={formPeriodStart} onDateChange={setFormPeriodStart} />
              </div>

              <div className="space-y-2">
                <Label>Billing Period End *</Label>
                <DatePicker date={formPeriodEnd} onDateChange={setFormPeriodEnd} />
              </div>
            </div>

            {/* Show billing days preview */}
            {formPeriodStart && formPeriodEnd && formPeriodStart < formPeriodEnd && (
              <p className="text-sm text-muted-foreground">
                Billing period: {differenceInDays(formPeriodEnd, formPeriodStart) + 1} days
              </p>
            )}

            {/* Conditional fields based on utility type */}
            {formType === 'rates' ? (
              // Rates: Fixed cost only (no usage metering)
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="cost">Cost *</Label>
                  <Input
                    id="cost"
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={formCost}
                    onChange={(e) => setFormCost(e.target.value)}
                    placeholder="0.00"
                  />
                </div>
                <p className="text-sm text-muted-foreground italic">
                  Council rates are a fixed cost with no usage metering
                </p>
              </div>
            ) : (
              // Metered utilities: Usage + Unit + Cost
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="usage">Usage *</Label>
                  <Input
                    id="usage"
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={formUsage}
                    onChange={(e) => setFormUsage(e.target.value)}
                    placeholder={formType === 'gas' ? 'Number of bottles' : '0.00'}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="unit">Unit *</Label>
                  <Input
                    id="unit"
                    value={formUnit}
                    onChange={(e) => setFormUnit(e.target.value)}
                    placeholder={formType === 'gas' ? 'bottles' : 'kWh, m³'}
                    maxLength={50}
                  />
                  {formType === 'gas' && (
                    <p className="text-xs text-muted-foreground">
                      e.g., "bottles" for 45kg cylinders
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="cost">Cost *</Label>
                  <Input
                    id="cost"
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={formCost}
                    onChange={(e) => setFormCost(e.target.value)}
                    placeholder="0.00"
                  />
                </div>
              </div>
            )}

            {/* Solar feed-in section (electricity only) */}
            {formType === 'electricity' && (
              <div className="border rounded-lg p-4 space-y-3 bg-green-50/50">
                <Label className="text-sm font-medium text-green-800">
                  ☀️ Solar Feed-In (Optional)
                </Label>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="solarFeedIn" className="text-sm">Feed-In (kWh)</Label>
                    <Input
                      id="solarFeedIn"
                      type="number"
                      min="0"
                      step="0.01"
                      value={formSolarFeedIn}
                      onChange={(e) => setFormSolarFeedIn(e.target.value)}
                      placeholder="kWh exported to grid"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="solarCredit" className="text-sm">Credit Received ($)</Label>
                    <Input
                      id="solarCredit"
                      type="number"
                      min="0"
                      step="0.01"
                      value={formSolarFeedInCredit}
                      onChange={(e) => setFormSolarFeedInCredit(e.target.value)}
                      placeholder="Credit on bill"
                    />
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  Enter the kWh you exported to the grid and the credit amount shown on your bill
                </p>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Input
                id="notes"
                value={formNotes}
                onChange={(e) => setFormNotes(e.target.value)}
                placeholder="Optional notes"
                maxLength={500}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCloseDialog}>
              Cancel
            </Button>
            <LoadingButton onClick={handleSubmit} loading={submitting}>
              {editingUtility ? 'Update' : 'Create'}
            </LoadingButton>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      {deleteUtility && (
        <ConfirmDialog
          open={!!deleteUtility}
          onOpenChange={(open) => !open && setDeleteUtility(null)}
          onConfirm={handleDelete}
          title="Delete Utility Entry?"
          description={`Are you sure you want to delete the ${deleteUtility.utility_type} bill from ${deleteUtility.provider}?`}
          confirmText="Delete"
          variant="destructive"
        />
      )}
      </TabsContent>

      <TabsContent value="graphs">
        <UtilityGraphs selectedType={typeFilter !== 'all' ? (typeFilter as UtilityType) : null} />
      </TabsContent>
    </Tabs>
  );
}
