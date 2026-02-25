import { useEffect, useState } from 'react';
import { format, subMonths, startOfMonth, endOfMonth } from 'date-fns';
import { useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { financialService } from '@/services/financialService';
import { dashboardService } from '@/services/dashboardService';
import type { UtilityStatsResponse } from '@/services/financialService';
import type { AlertsWidget, PrioritiesWidget } from '@/services/dashboardService';
import { formatCurrency } from '@/lib/frequencyUtils';
import {
  Zap, Flame, Droplet, Home,
  AlertTriangle, ListTodo, ExternalLink
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

// Last 12 months date range
const getLast12Months = () => {
  const now = new Date();
  return {
    start_date: format(startOfMonth(subMonths(now, 11)), 'yyyy-MM-dd'),
    end_date: format(endOfMonth(now), 'yyyy-MM-dd'),
  };
};

export default function Dashboard() {
  const { user } = useAuthStore();

  // Utility stats (last 12 months)
  const [electricityStats, setElectricityStats] = useState<UtilityStatsResponse | null>(null);
  const [gasStats, setGasStats] = useState<UtilityStatsResponse | null>(null);
  const [waterStats, setWaterStats] = useState<UtilityStatsResponse | null>(null);
  const [ratesStats, setRatesStats] = useState<UtilityStatsResponse | null>(null);
  const [utilitiesLoading, setUtilitiesLoading] = useState(true);

  // Priorities
  const [priorities, setPriorities] = useState<PrioritiesWidget | null>(null);
  const [prioritiesLoading, setPrioritiesLoading] = useState(true);

  // Alerts
  const [alerts, setAlerts] = useState<AlertsWidget | null>(null);
  const [alertsLoading, setAlertsLoading] = useState(true);

  useEffect(() => {
    const dateRange = getLast12Months();

    // All 4 utility stats in parallel
    Promise.allSettled([
      financialService.utilities.stats('electricity', dateRange),
      financialService.utilities.stats('gas', dateRange),
      financialService.utilities.stats('water', dateRange),
      financialService.utilities.stats('rates', dateRange),
    ]).then(([elec, gas, water, rates]) => {
      if (elec.status === 'fulfilled') setElectricityStats(elec.value);
      if (gas.status === 'fulfilled') setGasStats(gas.value);
      if (water.status === 'fulfilled') setWaterStats(water.value);
      if (rates.status === 'fulfilled') setRatesStats(rates.value);
    }).finally(() => setUtilitiesLoading(false));

    // Priorities
    dashboardService.priorities(5)
      .then(setPriorities)
      .catch(() => {})
      .finally(() => setPrioritiesLoading(false));

    // Alerts
    dashboardService.alerts()
      .then(setAlerts)
      .catch(() => {})
      .finally(() => setAlertsLoading(false));
  }, []);

  const totalAlerts = alerts
    ? alerts.insurance_renewals.urgent + alerts.document_expiries.urgent +
      alerts.insurance_renewals.upcoming + alerts.document_expiries.upcoming +
      alerts.quote_expiries
    : 0;

  return (
    <div>
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user?.full_name}!
        </h1>
        <p className="text-gray-600">Your home management dashboard</p>
      </div>

      {/* ── Financial Overview ───────────────────────────────────── */}
      <h2 className="text-lg font-semibold text-gray-700 mb-3">Financial</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {/* Alerts / Expiring */}
        <Card className={totalAlerts > 0 ? 'border-amber-300' : ''}>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <AlertTriangle className={`h-4 w-4 ${totalAlerts > 0 ? 'text-amber-500' : 'text-gray-400'}`} />
              Expiring / Renewals
            </CardTitle>
            <CardDescription>Insurance, documents & quotes</CardDescription>
          </CardHeader>
          <CardContent>
            {alertsLoading ? (
              <div className="text-sm text-gray-500">Loading...</div>
            ) : alerts ? (
              totalAlerts === 0 ? (
                <p className="text-sm text-green-600 font-medium">✅ Nothing expiring soon</p>
              ) : (
                <div className="space-y-2 text-sm">
                  {alerts.insurance_renewals.urgent > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-red-600 font-medium">Insurance (within 7 days)</span>
                      <Badge variant="destructive">{alerts.insurance_renewals.urgent}</Badge>
                    </div>
                  )}
                  {alerts.insurance_renewals.upcoming > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-amber-600">Insurance (7–30 days)</span>
                      <Badge className="bg-amber-100 text-amber-800">{alerts.insurance_renewals.upcoming}</Badge>
                    </div>
                  )}
                  {alerts.document_expiries.urgent > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-red-600 font-medium">Documents (within 7 days)</span>
                      <Badge variant="destructive">{alerts.document_expiries.urgent}</Badge>
                    </div>
                  )}
                  {alerts.document_expiries.upcoming > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-amber-600">Documents (7–30 days)</span>
                      <Badge className="bg-amber-100 text-amber-800">{alerts.document_expiries.upcoming}</Badge>
                    </div>
                  )}
                  {alerts.quote_expiries > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Quotes expiring</span>
                      <Badge variant="secondary">{alerts.quote_expiries}</Badge>
                    </div>
                  )}
                  <a href="/assets" className="text-xs text-blue-600 hover:underline flex items-center gap-1 pt-1">
                    View in Assets <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )
            ) : (
              <p className="text-sm text-gray-500">Unable to load alerts</p>
            )}
          </CardContent>
        </Card>

        {/* Top 5 Priorities */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <ListTodo className="h-4 w-4 text-blue-500" />
              Top Priorities
            </CardTitle>
            <CardDescription>
              {priorities ? `${priorities.total_priorities} pending items` : 'Home improvement items'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {prioritiesLoading ? (
              <div className="text-sm text-gray-500">Loading...</div>
            ) : priorities && priorities.top_priorities.length > 0 ? (
              <div className="space-y-2">
                {priorities.top_priorities.map((item, i) => (
                  <div key={item.id} className="flex items-start justify-between gap-2 text-sm">
                    <div className="flex items-start gap-2 min-w-0">
                      <span className="text-gray-400 font-mono text-xs mt-0.5 shrink-0">#{i + 1}</span>
                      <span className="text-gray-800 truncate">{item.name}</span>
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <Badge variant="secondary" className="text-xs">{item.net_score.toFixed(1)}</Badge>
                      <span className="text-xs text-gray-400">{formatCurrency(item.estimated_cost)}</span>
                    </div>
                  </div>
                ))}
                <a href="/projects" className="text-xs text-blue-600 hover:underline flex items-center gap-1 pt-1">
                  View all priorities <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            ) : (
              <p className="text-sm text-gray-500">
                No priorities yet. <a href="/projects" className="text-blue-600 hover:underline">Add items</a>
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ── Utilities (Last 12 Months) ───────────────────────────── */}
      <h2 className="text-lg font-semibold text-gray-700 mb-3">Utilities — Last 12 Months</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <UtilityWidget
          label="Electricity"
          icon={<Zap className="h-4 w-4 text-yellow-500" />}
          stats={electricityStats}
          loading={utilitiesLoading}
          color="yellow"
          href="/financial"
          unit="kWh"
        />
        <UtilityWidget
          label="Gas"
          icon={<Flame className="h-4 w-4 text-orange-500" />}
          stats={gasStats}
          loading={utilitiesLoading}
          color="orange"
          href="/financial"
          unit="units"
        />
        <UtilityWidget
          label="Water"
          icon={<Droplet className="h-4 w-4 text-blue-500" />}
          stats={waterStats}
          loading={utilitiesLoading}
          color="blue"
          href="/financial"
          unit="kL"
        />
        <UtilityWidget
          label="Rates"
          icon={<Home className="h-4 w-4 text-gray-500" />}
          stats={ratesStats}
          loading={utilitiesLoading}
          color="gray"
          href="/financial"
          isRates
        />
      </div>

      {/* ── Account Info ─────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Account</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-500 mb-1">Username</p>
              <p className="font-medium">{user?.username}</p>
            </div>
            <div>
              <p className="text-gray-500 mb-1">Email</p>
              <p className="font-medium">{user?.email}</p>
            </div>
            <div>
              <p className="text-gray-500 mb-1">Role</p>
              <p className="font-medium capitalize">{user?.role?.toLowerCase()}</p>
            </div>
            <div>
              <p className="text-gray-500 mb-1">MFA</p>
              <p className="font-medium">{user?.mfa_enabled ? '✅ Enabled' : '❌ Disabled'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ── Utility Widget Component ─────────────────────────────────────────────────

interface UtilityWidgetProps {
  label: string;
  icon: React.ReactNode;
  stats: UtilityStatsResponse | null;
  loading: boolean;
  color: 'yellow' | 'orange' | 'blue' | 'gray';
  href: string;
  unit?: string;
  isRates?: boolean;
}

const colorMap = {
  yellow: 'bg-yellow-100 border-yellow-300',
  orange: 'bg-orange-100 border-orange-300',
  blue: 'bg-blue-100 border-blue-300',
  gray: 'bg-gray-100 border-gray-300',
};

function UtilityWidget({ label, icon, stats, loading, color, href, unit, isRates }: UtilityWidgetProps) {
  const hasData = stats && stats.entry_count > 0;

  return (
    <Card className={`${colorMap[color]} border`}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          {icon}
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-xs text-gray-500">Loading...</div>
        ) : hasData ? (
          <div className="space-y-1">
            {isRates ? (
              <div>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.average_cost)}</p>
                <p className="text-xs text-gray-500">avg bill cost</p>
              </div>
            ) : (
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.avg_daily_usage.toFixed(2)}
                  <span className="text-sm font-normal text-gray-500 ml-1">{unit}/day</span>
                </p>
                <p className="text-xs text-gray-500">avg daily usage</p>
              </div>
            )}
            <div className="pt-1 border-t border-gray-200">
              <p className="text-sm text-gray-600">{formatCurrency(stats.average_cost)} avg / bill</p>
              <p className="text-xs text-gray-400">{stats.entry_count} bills recorded</p>
            </div>
            <a href={href} className="text-xs text-blue-600 hover:underline flex items-center gap-1 pt-1">
              View details <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        ) : (
          <div>
            <p className="text-xs text-gray-500 mb-2">No data in last 12 months</p>
            <a href={href} className="text-xs text-blue-600 hover:underline">Add entry</a>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
