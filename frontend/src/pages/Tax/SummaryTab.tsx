import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { PageLoader } from '@/components/common/PageLoader';
import { taxService } from '@/services/taxService';
import type { WFHSummary, TravelSummary } from '@/services/taxService';
import { getErrorMessage } from '@/lib/errorMessages';
import { toast } from 'sonner';

type SummaryTabProps = Readonly<{
  financialYear: string;
}>

export function SummaryTab({ financialYear }: SummaryTabProps) {
  const [wfhSummary, setWfhSummary] = useState<WFHSummary | null>(null);
  const [travelSummary, setTravelSummary] = useState<TravelSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [exportingWFH, setExportingWFH] = useState(false);
  const [exportingTravel, setExportingTravel] = useState(false);

  // ATO Rate state (not saved, just for calculation)
  const [wfhRate, setWfhRate] = useState<string>('0.67');
  const [travelRate, setTravelRate] = useState<string>('0.85');

  // Fetch summaries
  const fetchSummaries = async () => {
    setLoading(true);
    try {
      const wfhRateNum = Number.parseFloat(wfhRate) || 0.67;
      const travelRateNum = Number.parseFloat(travelRate) || 0.85;

      console.log('[Summary] Fetching for FY:', financialYear, 'WFH rate:', wfhRateNum, 'Travel rate:', travelRateNum);

      const [wfh, travel] = await Promise.all([
        taxService.wfh.summary(financialYear, wfhRateNum).catch((err) => { console.error('[Summary] WFH error:', err); return null; }),
        taxService.travel.summary(financialYear, travelRateNum).catch((err) => { console.error('[Summary] Travel error:', err); return null; }),
      ]);

      console.log('[Summary] WFH data:', wfh);
      console.log('[Summary] Travel data:', travel);

      setWfhSummary(wfh);
      setTravelSummary(travel);
    } catch (error) {
      console.error('Error fetching summaries:', error);
      // Don't show error toast for empty data scenarios
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummaries();
  }, [financialYear]);

  const handleRecalculate = () => {
    fetchSummaries();
  };

  const handleExportWFH = async () => {
    setExportingWFH(true);
    try {
      const wfhRateNum = Number.parseFloat(wfhRate) || 0.67;
      const blob = await taxService.wfh.export(financialYear, wfhRateNum);
      const url = globalThis.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `wfh-${financialYear}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      globalThis.URL.revokeObjectURL(url);
      toast.success('WFH export downloaded');
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setExportingWFH(false);
    }
  };

  const handleExportTravel = async () => {
    setExportingTravel(true);
    try {
      const travelRateNum = Number.parseFloat(travelRate) || 0.85;
      const blob = await taxService.travel.export(financialYear, travelRateNum);
      const url = globalThis.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `travel-${financialYear}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      globalThis.URL.revokeObjectURL(url);
      toast.success('Travel export downloaded');
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setExportingTravel(false);
    }
  };

  if (loading) {
    return <PageLoader message="Loading summary..." />;
  }

  const grandTotal = (wfhSummary?.total_deduction || 0) + (travelSummary?.total_deduction || 0);

  return (
    <div className="space-y-6">
      {/* Grand Total */}
      <Card className="border-primary">
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardDescription>Total Tax Deductions - FY {financialYear}</CardDescription>
              <CardTitle className="text-4xl">${grandTotal.toFixed(2)}</CardTitle>
            </div>
            <Button onClick={handleRecalculate} disabled={loading}>
              {loading ? 'Calculating...' : 'Recalculate'}
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Summary Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* WFH Summary */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Work From Home</CardTitle>
                <CardDescription>
                  {wfhSummary ? `${format(new Date(wfhSummary.fy_start_date), 'PP')} - ${format(new Date(wfhSummary.fy_end_date), 'PP')}` : `FY ${financialYear}`}
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportWFH}
                disabled={exportingWFH || !wfhSummary?.total_days}
              >
                <Download className="mr-2 h-4 w-4" />
                {exportingWFH ? 'Exporting...' : 'Export'}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Days</p>
                <p className="text-2xl font-bold">{wfhSummary?.total_days || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Hours</p>
                <p className="text-2xl font-bold">{wfhSummary ? wfhSummary.total_hours.toFixed(1) : '0.0'}</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-2">ATO Rate ($/hour)</p>
              <div className="flex items-center gap-2">
                <span className="text-lg font-medium">$</span>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={wfhRate}
                  onChange={(e) => setWfhRate(e.target.value)}
                  className="w-24"
                />
                <span className="text-sm text-gray-500">per hour</span>
              </div>
            </div>
            <div className="pt-2 border-t">
              <p className="text-sm text-gray-600">Total Deduction</p>
              <p className="text-2xl font-bold text-primary">${wfhSummary ? wfhSummary.total_deduction.toFixed(2) : '0.00'}</p>
            </div>
          </CardContent>
        </Card>

        {/* Travel Summary */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Work Travel</CardTitle>
                <CardDescription>
                  {travelSummary ? `${format(new Date(travelSummary.fy_start_date), 'PP')} - ${format(new Date(travelSummary.fy_end_date), 'PP')}` : `FY ${financialYear}`}
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportTravel}
                disabled={exportingTravel || !travelSummary?.total_trips}
              >
                <Download className="mr-2 h-4 w-4" />
                {exportingTravel ? 'Exporting...' : 'Export'}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Trips</p>
                <p className="text-2xl font-bold">{travelSummary?.total_trips || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Distance</p>
                <p className="text-2xl font-bold">{travelSummary ? travelSummary.total_km.toFixed(1) : '0.0'} km</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-2">ATO Rate ($/km)</p>
              <div className="flex items-center gap-2">
                <span className="text-lg font-medium">$</span>
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  value={travelRate}
                  onChange={(e) => setTravelRate(e.target.value)}
                  className="w-24"
                />
                <span className="text-sm text-gray-500">per km</span>
              </div>
            </div>
            <div className="pt-2 border-t">
              <p className="text-sm text-gray-600">Total Deduction</p>
              <p className="text-2xl font-bold text-primary">${travelSummary ? travelSummary.total_deduction.toFixed(2) : '0.00'}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ATO Information */}
      <Card>
        <CardHeader>
          <CardTitle>ATO Compliance Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-gray-600">
          <p>
            <strong>Record Retention:</strong> All tax records must be retained for 5 years from the date of lodgment of the tax return in which the deduction is claimed.
          </p>
          <p>
            <strong>Work From Home:</strong> You can claim a deduction for the expenses incurred when working from home, including electricity, phone, internet, and computer consumables.
          </p>
          <p>
            <strong>Work Travel:</strong> You can claim deductions for work-related car expenses if you use your own car or a leased car. This includes travel between workplaces and work-related errands.
          </p>
          <p className="text-xs mt-4 text-gray-500">
            The rates shown are based on ATO guidelines. Always consult with a registered tax agent or the ATO for specific advice regarding your tax situation.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
