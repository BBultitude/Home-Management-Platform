import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">🏠 Home Management Platform</h1>
            <p className="text-sm text-gray-600">v1.0.0 - Production</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
              <p className="text-xs text-gray-500">{user?.role}</p>
            </div>
            <Button variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.full_name}!
          </h2>
          <p className="text-gray-600">
            Your home management dashboard
          </p>
        </div>

        {/* Dashboard Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Tax Management</CardTitle>
              <CardDescription>Work from home and travel deductions</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">Track your tax-deductible expenses</p>
              <Button className="mt-4 w-full" variant="outline">
                View Tax Records
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Financial Overview</CardTitle>
              <CardDescription>Income, expenses, and budgets</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">Manage your household finances</p>
              <Button className="mt-4 w-full" variant="outline">
                View Finances
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Assets & Documents</CardTitle>
              <CardDescription>Insurance, properties, and files</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">Track important documents and assets</p>
              <Button className="mt-4 w-full" variant="outline">
                View Assets
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Projects</CardTitle>
              <CardDescription>Home improvement tracking</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">Manage home projects and quotes</p>
              <Button className="mt-4 w-full" variant="outline">
                View Projects
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Knowledge Base</CardTitle>
              <CardDescription>Household reference information</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">Store measurements, paint codes, and more</p>
              <Button className="mt-4 w-full" variant="outline">
                View Knowledge Base
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Meal Planner</CardTitle>
              <CardDescription>Weekly meal planning</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">Plan meals and manage recipes</p>
              <Button className="mt-4 w-full" variant="outline">
                View Meal Plans
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Quick Stats */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle>System Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Username</p>
                  <p className="font-medium">{user?.username}</p>
                </div>
                <div>
                  <p className="text-gray-600">Email</p>
                  <p className="font-medium">{user?.email}</p>
                </div>
                <div>
                  <p className="text-gray-600">Role</p>
                  <p className="font-medium">{user?.role}</p>
                </div>
                <div>
                  <p className="text-gray-600">MFA Status</p>
                  <p className="font-medium">{user?.mfa_enabled ? 'Enabled' : 'Disabled'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
