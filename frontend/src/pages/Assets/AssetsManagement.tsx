import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import InsurancePoliciesTab from './InsurancePoliciesTab';
import DocumentsTab from './DocumentsTab';

export default function AssetsManagement() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Assets & Documents</h1>
        <p className="text-gray-500 mt-2">
          Manage insurance policies and important household documents
        </p>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="insurance" className="space-y-6">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="insurance">Insurance Policies</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
        </TabsList>

        <TabsContent value="insurance">
          <InsurancePoliciesTab />
        </TabsContent>

        <TabsContent value="documents">
          <DocumentsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
