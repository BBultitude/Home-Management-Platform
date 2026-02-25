import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useAuthStore } from '@/stores/authStore';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  mfa_enabled: boolean;
}

export default function AdminUsers() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [resetMfaUserId, setResetMfaUserId] = useState<number | null>(null);
  const [deleteUserId, setDeleteUserId] = useState<number | null>(null);

  // Create user form state
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'Reader',
  });

  // Check if current user is admin
  useEffect(() => {
    if (user?.role?.toUpperCase() !== 'ADMIN') {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  // Fetch users
  const fetchUsers = async () => {
    setLoading(true);
    setError('');
    try {
      const response: any = await apiClient.get('/admin/users');
      // Backend returns { users: [...], total: number, limit: number, offset: number }
      const usersList = response?.users || [];
      setUsers(Array.isArray(usersList) ? usersList : []);
    } catch (err: any) {
      console.error('Failed to fetch users:', err);
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Create new user
  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      await apiClient.post('/auth/register', newUser);
      setSuccess(`User ${newUser.username} created successfully`);
      setNewUser({ username: '', email: '', password: '', full_name: '', role: 'VIEWER' });
      setShowCreateForm(false);
      fetchUsers();
    } catch (err: any) {
      console.error('Failed to create user:', err);

      // Parse Pydantic validation errors
      let errorMessage = 'Failed to create user';
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          // Pydantic validation errors
          errorMessage = detail.map((e: any) => e.msg || e.message).join('; ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        }
      }
      setError(errorMessage);
    }
  };

  // Reset MFA for a user
  const handleResetMfa = async () => {
    if (resetMfaUserId === null) return;
    try {
      await apiClient.post(`/admin/users/${resetMfaUserId}/reset-mfa`);
      toast.success('MFA reset successfully. The user will be prompted to set up MFA on next login.');
      setResetMfaUserId(null);
      fetchUsers();
    } catch (err: any) {
      console.error('Failed to reset MFA:', err);
      toast.error('Failed to reset MFA');
    }
  };

  // Delete user
  const handleDeleteUser = async () => {
    if (deleteUserId === null) return;
    try {
      await apiClient.delete(`/admin/users/${deleteUserId}`);
      toast.success('User deleted successfully.');
      setDeleteUserId(null);
      fetchUsers();
    } catch (err: any) {
      console.error('Failed to delete user:', err);
      toast.error('Failed to delete user');
    }
  };

  // Toggle user active status
  const handleToggleActive = async (userId: number, currentStatus: boolean) => {
    try {
      await apiClient.put(`/admin/users/${userId}`, { is_active: !currentStatus });
      setSuccess(`User ${currentStatus ? 'deactivated' : 'activated'} successfully`);
      fetchUsers();
    } catch (err: any) {
      console.error('Failed to update user:', err);
      setError('Failed to update user status');
    }
  };

  if (loading) {
    return <p className="text-center text-gray-600">Loading users...</p>;
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
        <p className="text-gray-600 mt-1">Manage user accounts and permissions</p>
      </div>

      {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-4 bg-green-50 border-green-300 text-green-800">
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {/* Create User Form */}
        {showCreateForm ? (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Create New User</CardTitle>
              <CardDescription>Add a new user to the system</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateUser} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="username">Username *</Label>
                    <Input
                      id="username"
                      value={newUser.username}
                      onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newUser.email}
                      onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="full_name">Full Name *</Label>
                    <Input
                      id="full_name"
                      value={newUser.full_name}
                      onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="role">Role *</Label>
                    <select
                      id="role"
                      value={newUser.role}
                      onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                      className="w-full h-10 px-3 rounded-md border border-gray-300 bg-white"
                      required
                    >
                      <option value="Reader">Reader (Read-only)</option>
                      <option value="Editor">Editor (Can modify)</option>
                      <option value="Admin">Admin (Full access)</option>
                    </select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="password">Password *</Label>
                  <Input
                    id="password"
                    type="password"
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    required
                    minLength={12}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Must meet NIST requirements: 12+ chars, uppercase, lowercase, digit
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button type="submit">Create User</Button>
                  <Button type="button" variant="outline" onClick={() => setShowCreateForm(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        ) : (
          <div className="mb-6">
            <Button onClick={() => setShowCreateForm(true)}>+ Create New User</Button>
          </div>
        )}

        {/* Users List */}
        <Card>
          <CardHeader>
            <CardTitle>Users ({users.length})</CardTitle>
            <CardDescription>Manage system users</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b">
                  <tr className="text-left">
                    <th className="pb-2 font-medium">Username</th>
                    <th className="pb-2 font-medium">Full Name</th>
                    <th className="pb-2 font-medium">Email</th>
                    <th className="pb-2 font-medium">Role</th>
                    <th className="pb-2 font-medium">Status</th>
                    <th className="pb-2 font-medium">MFA</th>
                    <th className="pb-2 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="border-b">
                      <td className="py-3">{u.username}</td>
                      <td className="py-3">{u.full_name}</td>
                      <td className="py-3">{u.email}</td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded text-xs ${
                          u.role === 'ADMIN' ? 'bg-red-100 text-red-800' :
                          u.role === 'EDITOR' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded text-xs ${
                          u.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="py-3">{u.mfa_enabled ? '✅' : '❌'}</td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleToggleActive(u.id, u.is_active)}
                          >
                            {u.is_active ? 'Deactivate' : 'Activate'}
                          </Button>
                          {u.mfa_enabled && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setResetMfaUserId(u.id)}
                            >
                              Reset MFA
                            </Button>
                          )}
                          {u.id !== user?.id && (
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => setDeleteUserId(u.id)}
                            >
                              Delete
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

      <AlertDialog open={deleteUserId !== null} onOpenChange={(open) => !open && setDeleteUserId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete User?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete all data for this user including tax records. Ensure ATO
              5-year retention is met before proceeding. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteUser} className="bg-red-600 hover:bg-red-700">
              Delete User
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={resetMfaUserId !== null} onOpenChange={(open) => !open && setResetMfaUserId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Reset MFA?</AlertDialogTitle>
            <AlertDialogDescription>
              This will clear the user's MFA. They will be prompted to set up MFA again on their next login. Continue?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleResetMfa}>Reset MFA</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
