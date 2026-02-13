import { Button } from '@/components/ui/button'

function App() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-foreground">
            🏠 Home Management Platform
          </h1>
          <p className="text-lg text-muted-foreground">
            v1.0.0 - Frontend Foundation (Sprint 12)
          </p>
        </header>

        <div className="bg-card border border-border rounded-lg p-6 space-y-6">
          <h2 className="text-2xl font-semibold">✅ Setup Complete</h2>

          <div className="space-y-4">
            <div className="space-y-2">
              <h3 className="text-lg font-medium">Core Technologies:</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>React 18 + TypeScript</li>
                <li>Vite (build tool)</li>
                <li>Tailwind CSS 3</li>
                <li>shadcn/ui components</li>
                <li>React Router v6</li>
                <li>TanStack Query</li>
                <li>Zustand</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-medium">Project Structure:</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>components/ - UI components</li>
                <li>lib/ - Utilities and helpers</li>
                <li>hooks/ - Custom React hooks</li>
                <li>services/ - API services</li>
                <li>stores/ - State management</li>
                <li>pages/ - Route pages</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-medium">Component Library Demo:</h3>
              <div className="flex flex-wrap gap-2">
                <Button>Default Button</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="destructive">Destructive</Button>
                <Button size="sm">Small</Button>
                <Button size="lg">Large</Button>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-primary/10 border border-primary/20 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">🚀 Next Steps</h3>
          <ol className="list-decimal list-inside space-y-1 text-sm">
            <li>Create authentication pages (Login, MFA)</li>
            <li>Build AppShell layout (Header, Sidebar)</li>
            <li>Implement routing structure</li>
            <li>Set up API client with interceptors</li>
            <li>Create auth state management</li>
            <li>Build dashboard widgets</li>
          </ol>
        </div>
      </div>
    </div>
  )
}

export default App
