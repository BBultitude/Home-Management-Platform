import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import PrioritiesTab from './PrioritiesTab';
import ProjectsTab from './ProjectsTab';
import QuotesTab from './QuotesTab';

export default function ProjectsManagement() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Projects & Tasks</h1>
        <p className="text-gray-500 mt-2">
          Prioritize repairs, manage home improvement projects, and track contractor quotes
        </p>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="priorities" className="space-y-6">
        <TabsList className="grid w-full max-w-2xl grid-cols-3">
          <TabsTrigger value="priorities">Priority Items</TabsTrigger>
          <TabsTrigger value="projects">Projects</TabsTrigger>
          <TabsTrigger value="quotes">Quotes</TabsTrigger>
        </TabsList>

        <TabsContent value="priorities">
          <PrioritiesTab />
        </TabsContent>

        <TabsContent value="projects">
          <ProjectsTab />
        </TabsContent>

        <TabsContent value="quotes">
          <QuotesTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
