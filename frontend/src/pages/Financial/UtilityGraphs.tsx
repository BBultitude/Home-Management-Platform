import { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle
} from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { DatePicker } from '@/components/forms/DatePicker';
import { TrendingUp, TrendingDown, BarChart3, Users, Calendar } from 'lucide-react';
import { financialService } from '@/services/financialService';
import type { UtilityType, UtilityGraphsResponse } from '@/services/financialService';
import { formatCurrency } from '@/lib/frequencyUtils';
import { toast } from 'sonner';
import { format, subMonths, startOfMonth, endOfMonth } from 'date-fns';

type PeriodType = 'last12' | 'prior12' | 'custom';

interface UtilityGraphsProps {
  selectedType: UtilityType | null;
}

export default function UtilityGraphs({ selectedType }: UtilityGraphsProps) {
  const [graphData, setGraphData] = useState<UtilityGraphsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState<PeriodType>('last12');
  const [customStartDate, setCustomStartDate] = useState<Date | undefined>(undefined);
  const [customEndDate, setCustomEndDate] = useState<Date | undefined>(undefined);

  const calculateDateRange = (): { start_date?: string; end_date?: string } => {
    const now = new Date();

    switch (period) {
      case 'last12':
        // Last 12 months from today
        const last12Start = startOfMonth(subMonths(now, 11));
        const last12End = endOfMonth(now);
        return {
          start_date: format(last12Start, 'yyyy-MM-dd'),
          end_date: format(last12End, 'yyyy-MM-dd')
        };

      case 'prior12':
        // Months 13-24 ago
        const prior12Start = startOfMonth(subMonths(now, 23));
        const prior12End = endOfMonth(subMonths(now, 12));
        return {
          start_date: format(prior12Start, 'yyyy-MM-dd'),
          end_date: format(prior12End, 'yyyy-MM-dd')
        };

      case 'custom':
        // Custom date range
        if (!customStartDate && !customEndDate) {
          return {};
        }
        return {
          start_date: customStartDate ? format(customStartDate, 'yyyy-MM-dd') : undefined,
          end_date: customEndDate ? format(customEndDate, 'yyyy-MM-dd') : undefined
        };

      default:
        return {};
    }
  };

  const loadGraphData = async (type: UtilityType) => {
    setLoading(true);
    try {
      const dateRange = calculateDateRange();
      const data = await financialService.utilities.graphs(type, dateRange);
      setGraphData(data);
    } catch (error: any) {
      console.error('Failed to load graph data:', error);
      toast.error('Failed to load graph data');
    } finally {
      setLoading(false);
    }
  };

  const handleTypeChange = (type: UtilityType) => {
    loadGraphData(type);
  };

  // Load data when component mounts or selectedType/period changes
  useEffect(() => {
    if (selectedType) {
      loadGraphData(selectedType);
    }
  }, [selectedType, period, customStartDate, customEndDate]);

  if (!selectedType && !graphData) {
    return (
      <Card className="bg-white dark:bg-white">
        <CardHeader>
          <CardTitle>Utility Usage & Cost Analytics</CardTitle>
          <CardDescription>
            Select a utility type to view detailed cost and usage graphs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="w-full max-w-xs">
              <Select onValueChange={(value) => handleTypeChange(value as UtilityType)}>
                <SelectTrigger className="bg-white dark:bg-white">
                  <SelectValue placeholder="Select utility type" />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-white">
                  <SelectItem value="electricity">⚡ Electricity</SelectItem>
                  <SelectItem value="gas">🔥 Gas</SelectItem>
                  <SelectItem value="water">💧 Water</SelectItem>
                  <SelectItem value="rates">🏠 Rates</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className="bg-white dark:bg-white">
        <CardContent className="pt-6">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!graphData || graphData.total_entries === 0) {
    return (
      <Card className="bg-white dark:bg-white">
        <CardHeader>
          <CardTitle>No Data Available</CardTitle>
          <CardDescription>
            Add some utility entries to see graphs and analytics
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const typeLabels: Record<UtilityType, string> = {
    electricity: '⚡ Electricity',
    gas: '🔥 Gas',
    water: '💧 Water',
    rates: '🏠 Rates',
  };

  const getPeriodDescription = (): string => {
    const now = new Date();
    switch (period) {
      case 'last12':
        const last12Start = startOfMonth(subMonths(now, 11));
        return `${format(last12Start, 'MMM yyyy')} - ${format(now, 'MMM yyyy')}`;
      case 'prior12':
        const prior12Start = startOfMonth(subMonths(now, 23));
        const prior12End = endOfMonth(subMonths(now, 12));
        return `${format(prior12Start, 'MMM yyyy')} - ${format(prior12End, 'MMM yyyy')}`;
      case 'custom':
        if (!customStartDate && !customEndDate) {
          return 'Select date range';
        }
        const start = customStartDate ? format(customStartDate, 'MMM yyyy') : 'Start';
        const end = customEndDate ? format(customEndDate, 'MMM yyyy') : 'End';
        return `${start} - ${end}`;
      default:
        return '';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Type Selector */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">
              {typeLabels[graphData.utility_type as UtilityType]} Analytics
            </h2>
            <p className="text-sm text-gray-500">
              {graphData.total_entries} entries analyzed
            </p>
          </div>
          <div className="w-64">
            <Select
              value={graphData.utility_type}
              onValueChange={(value) => handleTypeChange(value as UtilityType)}
            >
              <SelectTrigger className="bg-white dark:bg-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white dark:bg-white">
                <SelectItem value="electricity">⚡ Electricity</SelectItem>
                <SelectItem value="gas">🔥 Gas</SelectItem>
                <SelectItem value="water">💧 Water</SelectItem>
                <SelectItem value="rates">🏠 Rates</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Period Selector */}
        <Card className="bg-white dark:bg-white">
          <CardContent className="pt-6">
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-gray-500" />
                  <Label className="text-sm font-medium">Time Period:</Label>
                </div>
                <Select value={period} onValueChange={(value) => setPeriod(value as PeriodType)}>
                  <SelectTrigger className="w-64 bg-white dark:bg-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-white dark:bg-white">
                    <SelectItem value="last12">Last 12 Months</SelectItem>
                    <SelectItem value="prior12">Prior 12 Months (13-24 months ago)</SelectItem>
                    <SelectItem value="custom">Custom Date Range</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {period === 'custom' && (
                <div className="flex items-center gap-4 pl-7">
                  <div className="flex items-center gap-2">
                    <Label className="text-sm">From:</Label>
                    <DatePicker
                      date={customStartDate}
                      onDateChange={setCustomStartDate}
                      placeholder="Start date"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="text-sm">To:</Label>
                    <DatePicker
                      date={customEndDate}
                      onDateChange={setCustomEndDate}
                      placeholder="End date"
                    />
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Period Summary */}
      <Card className="bg-blue-50 dark:bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Analyzing Period</p>
            <p className="text-2xl font-bold text-blue-900">{getPeriodDescription()}</p>
          </div>
        </CardContent>
      </Card>

      {/* Average Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-white dark:bg-white">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Average Cost (Period)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {formatCurrency(graphData.rolling_12_month_avg_cost)}
            </div>
            <p className="text-xs text-gray-500 mt-1">per month</p>
          </CardContent>
        </Card>

        <Card className="bg-white dark:bg-white">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Average Usage (Period)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {graphData.rolling_12_month_avg_usage.toFixed(2)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {graphData.monthly_data[0]?.entry_count > 0
                ? `avg per month`
                : 'units per month'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Cost Over Time */}
      <Card className="bg-white dark:bg-white">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Cost Over Time
          </CardTitle>
          <CardDescription>
            Monthly cost trends for {typeLabels[graphData.utility_type as UtilityType]}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={graphData.monthly_data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                tickFormatter={(value: number | undefined) => value !== undefined ? `$${value}` : '$0'}
              />
              <Tooltip
                formatter={(value: number | undefined) => value !== undefined ? formatCurrency(value) : '$0.00'}
                labelFormatter={(label) => `Month: ${label}`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="cost"
                stroke="#3B82F6"
                strokeWidth={2}
                name="Total Cost"
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Usage Over Time */}
      <Card className="bg-white dark:bg-white">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Usage Over Time
          </CardTitle>
          <CardDescription>
            Monthly usage trends for {typeLabels[graphData.utility_type as UtilityType]}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={graphData.monthly_data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis />
              <Tooltip
                formatter={(value: number | undefined) => value !== undefined ? value.toFixed(2) : '0.00'}
                labelFormatter={(label) => `Month: ${label}`}
              />
              <Legend />
              <Bar
                dataKey="usage"
                fill="#10B981"
                name="Total Usage"
              />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Cost Per Unit Trend */}
      <Card className="bg-white dark:bg-white">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingDown className="h-5 w-5" />
            Cost Per Unit Trend
          </CardTitle>
          <CardDescription>
            Track rate changes over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={graphData.monthly_data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="month"
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                tickFormatter={(value: number | undefined) => value !== undefined ? `$${value.toFixed(3)}` : '$0.000'}
              />
              <Tooltip
                formatter={(value: number | undefined) => value !== undefined ? `$${value.toFixed(4)} per unit` : '$0.0000 per unit'}
                labelFormatter={(label) => `Month: ${label}`}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="cost_per_unit"
                stroke="#F59E0B"
                strokeWidth={2}
                name="Cost Per Unit"
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Provider Comparison */}
      {graphData.provider_comparison.length > 1 && (
        <Card className="bg-white dark:bg-white">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Provider Comparison
            </CardTitle>
            <CardDescription>
              Compare costs and usage across different providers
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {graphData.provider_comparison.map((provider) => (
                <div
                  key={provider.provider}
                  className="border rounded-lg p-4"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-lg">{provider.provider}</h3>
                    <span className="text-sm text-gray-500">
                      {provider.entry_count} {provider.entry_count === 1 ? 'entry' : 'entries'}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Total Cost</p>
                      <p className="font-semibold text-lg">
                        {formatCurrency(provider.total_cost)}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Total Usage</p>
                      <p className="font-semibold text-lg">
                        {provider.total_usage.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Avg Cost/Unit</p>
                      <p className="font-semibold text-lg">
                        ${provider.average_cost_per_unit.toFixed(4)}
                      </p>
                    </div>
                  </div>
                  {provider.period_start && provider.period_end && (
                    <p className="text-xs text-gray-500 mt-2">
                      {new Date(provider.period_start).toLocaleDateString()} - {new Date(provider.period_end).toLocaleDateString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
