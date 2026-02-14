import { useAuthStore } from '@/stores/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Dashboard() {
  const { user } = useAuthStore();

  return (
    <div>
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user?.full_name}!
        </h1>
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
            <p className="text-sm text-gray-600 mb-4">
              Track your tax-deductible expenses
            </p>
            <div className="text-2xl font-bold text-gray-900">Coming Soon</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Financial Overview</CardTitle>
            <CardDescription>Income, expenses, and budgets</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Manage your household finances
            </p>
            <div className="text-2xl font-bold text-gray-900">Coming Soon</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Assets & Documents</CardTitle>
            <CardDescription>Insurance, properties, and files</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Track important documents and assets
            </p>
            <div className="text-2xl font-bold text-gray-900">Coming Soon</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Projects</CardTitle>
            <CardDescription>Home improvement tracking</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Manage home projects and quotes
            </p>
            <div className="text-2xl font-bold text-gray-900">Coming Soon</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Knowledge Base</CardTitle>
            <CardDescription>Household reference information</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Store measurements, paint codes, and more
            </p>
            <div className="text-2xl font-bold text-gray-900">Coming Soon</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Meal Planner</CardTitle>
            <CardDescription>Weekly meal planning</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Plan meals and manage recipes
            </p>
            <div className="text-2xl font-bold text-gray-900">Coming Soon</div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-600 mb-1">Username</p>
                <p className="font-medium">{user?.username}</p>
              </div>
              <div>
                <p className="text-gray-600 mb-1">Email</p>
                <p className="font-medium">{user?.email}</p>
              </div>
              <div>
                <p className="text-gray-600 mb-1">Role</p>
                <p className="font-medium capitalize">{user?.role?.toLowerCase()}</p>
              </div>
              <div>
                <p className="text-gray-600 mb-1">MFA Status</p>
                <p className="font-medium">{user?.mfa_enabled ? '✅ Enabled' : '❌ Disabled'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
