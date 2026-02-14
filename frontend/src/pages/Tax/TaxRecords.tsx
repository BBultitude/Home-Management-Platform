import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FinancialYearPicker, getCurrentFinancialYear } from '@/components/forms/FinancialYearPicker';
import { WFHTab } from './WFHTab';
import { TravelTab } from './TravelTab';
import { SummaryTab } from './SummaryTab';

export default function TaxRecords() {
  const [selectedFY, setSelectedFY] = useState(getCurrentFinancialYear());

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Tax Records</h1>
        <p className="text-gray-600 mt-1">
          Track work from home hours and travel claims for ATO compliance
        </p>
      </div>

      {/* Financial Year Selector */}
      <div className="mb-6">
        <div className="w-64">
          <FinancialYearPicker value={selectedFY} onChange={setSelectedFY} />
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="wfh" className="space-y-6">
        <TabsList>
          <TabsTrigger value="wfh">Work From Home</TabsTrigger>
          <TabsTrigger value="travel">Work Travel</TabsTrigger>
          <TabsTrigger value="summary">Summary</TabsTrigger>
        </TabsList>

        <TabsContent value="wfh">
          <WFHTab financialYear={selectedFY} />
        </TabsContent>

        <TabsContent value="travel">
          <TravelTab financialYear={selectedFY} />
        </TabsContent>

        <TabsContent value="summary">
          <SummaryTab financialYear={selectedFY} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
