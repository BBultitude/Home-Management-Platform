import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuthStore } from '@/stores/authStore';
import { apiClient } from '@/lib/api';

export default function Settings() {
  const navigate = useNavigate();
  const { user, logout, setUser } = useAuthStore();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // MFA state
  const [mfaError, setMfaError] = useState('');
  const [mfaSuccess, setMfaSuccess] = useState('');
  const [showMFASetup, setShowMFASetup] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [mfaSecret, setMfaSecret] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [mfaLoading, setMfaLoading] = useState(false);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation - Match backend NIST requirements
    if (newPassword.length < 12) {
      setError('Password must be at least 12 characters');
      return;
    }

    if (newPassword.length > 128) {
      setError('Password must be less than 128 characters');
      return;
    }

    if (!/[A-Z]/.test(newPassword)) {
      setError('Password must contain at least one uppercase letter (A-Z)');
      return;
    }

    if (!/[a-z]/.test(newPassword)) {
      setError('Password must contain at least one lowercase letter (a-z)');
      return;
    }

    if (!/\d/.test(newPassword)) {
      setError('Password must contain at least one digit (0-9)');
      return;
    }

    // Check weak patterns
    const passwordLower = newPassword.toLowerCase();
    const weakPattern = /^[\d!@#$%^&*()_+=\-\[\]{};:,.<>?/\\|~`]*(password|admin|welcome|letmein|qwerty|monkey|dragon|master|login|user|homelab|docker|home)[\d!@#$%^&*()_+=\-\[\]{};:,.<>?/\\|~`]*$/;
    if (weakPattern.test(passwordLower)) {
      setError("Don't use common words (password, admin, etc.) with just numbers/symbols");
      return;
    }

    // Check sequential patterns
    if (/(12345|23456|34567|45678|56789|78901|67890|abcde|bcdef|qwerty|asdfg|zxcvb)/.test(passwordLower)) {
      setError('Avoid sequential patterns (12345, qwerty, etc.)');
      return;
    }

    // Check repeated characters
    if (/(.)\1{3,}/.test(newPassword)) {
      setError('Avoid repeated characters (aaaa, 1111, etc.)');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    setIsLoading(true);
    try {
      await apiClient.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });

      setSuccess('Password changed successfully! Please log in again.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');

      // Logout after 2 seconds
      setTimeout(async () => {
        await logout();
        navigate('/');
      }, 2000);
    } catch (err: any) {
      console.error('Password change error:', err);

      // Extract error message from various backend response formats
      let errorMessage = 'Failed to change password. Please check your current password.';

      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        // Pydantic validation errors are arrays
        if (Array.isArray(detail)) {
          errorMessage = detail.map((e: any) => e.msg || e.message).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (detail.msg) {
          errorMessage = detail.msg;
        }
      }

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // MFA Setup - Step 1: Request QR code
  const handleMFASetup = async () => {
    setMfaError('');
    setMfaSuccess('');
    setMfaLoading(true);
    try {
      const response: any = await apiClient.post('/mfa/setup');
      setQrCode(response.qr_code);
      setMfaSecret(response.secret);
      setShowMFASetup(true);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to setup MFA';
      setMfaError(errorMessage);
    } finally {
      setMfaLoading(false);
    }
  };

  // MFA Setup - Step 2: Verify and enable
  const handleMFAEnable = async (e: React.FormEvent) => {
    e.preventDefault();
    setMfaError('');
    setMfaSuccess('');
    setMfaLoading(true);
    try {
      await apiClient.post('/mfa/enable', {
        secret: mfaSecret,
        code: verificationCode,
      });
      setMfaSuccess('MFA enabled successfully!');
      setShowMFASetup(false);
      setVerificationCode('');
      setQrCode('');
      setMfaSecret('');
      // Update user state
      if (user) {
        setUser({ ...user, mfa_enabled: true });
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Invalid verification code';
      setMfaError(errorMessage);
    } finally {
      setMfaLoading(false);
    }
  };

  // MFA Disable
  const handleMFADisable = async () => {
    if (!confirm('Are you sure you want to disable MFA? This will revoke all trusted devices.')) {
      return;
    }
    setMfaError('');
    setMfaSuccess('');
    setMfaLoading(true);
    try {
      await apiClient.post('/mfa/disable');
      setMfaSuccess('MFA disabled successfully');
      // Update user state
      if (user) {
        setUser({ ...user, mfa_enabled: false });
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to disable MFA';
      setMfaError(errorMessage);
    } finally {
      setMfaLoading(false);
    }
  };

  return (
    <div>
      <div className="max-w-2xl mx-auto">

        {/* User Profile Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>User Profile</CardTitle>
            <CardDescription>Your account information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-sm font-medium text-gray-500">Username</Label>
              <p className="text-lg">{user?.username}</p>
            </div>
            <div>
              <Label className="text-sm font-medium text-gray-500">Email</Label>
              <p className="text-lg">{user?.email}</p>
            </div>
            <div>
              <Label className="text-sm font-medium text-gray-500">Full Name</Label>
              <p className="text-lg">{user?.full_name}</p>
            </div>
            <div>
              <Label className="text-sm font-medium text-gray-500">Role</Label>
              <p className="text-lg capitalize">{user?.role.toLowerCase()}</p>
            </div>
            <div>
              <Label className="text-sm font-medium text-gray-500">MFA Status</Label>
              <p className="text-lg">{user?.mfa_enabled ? '✅ Enabled' : '❌ Disabled'}</p>
            </div>
          </CardContent>
        </Card>

        {/* Change Password Card */}
        <Card>
          <CardHeader>
            <CardTitle>Change Password</CardTitle>
            <CardDescription>Update your password to keep your account secure</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {success && (
                <Alert className="bg-green-50 border-green-300 text-green-800">
                  <AlertDescription>{success}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="currentPassword">Current Password</Label>
                <Input
                  id="currentPassword"
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="newPassword">New Password</Label>
                <Input
                  id="newPassword"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={12}
                  maxLength={128}
                  autoComplete="new-password"
                />
                <div className="text-xs text-gray-600 space-y-1">
                  <p className="font-medium">Requirements (NIST-based):</p>
                  <ul className="list-disc list-inside space-y-0.5 ml-2">
                    <li>12-128 characters long</li>
                    <li>At least one uppercase letter (A-Z)</li>
                    <li>At least one lowercase letter (a-z)</li>
                    <li>At least one digit (0-9)</li>
                    <li>No common weak patterns (password123, admin2024, etc.)</li>
                    <li>No sequential patterns (12345, qwerty, etc.)</li>
                    <li>No repeated characters (aaaa, 1111, etc.)</li>
                  </ul>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={12}
                  autoComplete="new-password"
                />
              </div>

              <Button type="submit" disabled={isLoading} className="w-full">
                {isLoading ? 'Changing Password...' : 'Change Password'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* MFA Security Card */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Two-Factor Authentication (MFA)</CardTitle>
            <CardDescription>Add an extra layer of security to your account</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mfaError && (
              <Alert variant="destructive">
                <AlertDescription>{mfaError}</AlertDescription>
              </Alert>
            )}

            {mfaSuccess && (
              <Alert className="bg-green-50 border-green-300 text-green-800">
                <AlertDescription>{mfaSuccess}</AlertDescription>
              </Alert>
            )}

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">MFA Status:</p>
                <p className={`text-sm ${user?.mfa_enabled ? 'text-green-600' : 'text-gray-600'}`}>
                  {user?.mfa_enabled ? '✅ Enabled' : '❌ Disabled'}
                </p>
              </div>
              {!user?.mfa_enabled && !showMFASetup && (
                <Button onClick={handleMFASetup} disabled={mfaLoading}>
                  {mfaLoading ? 'Loading...' : 'Enable MFA'}
                </Button>
              )}
              {user?.mfa_enabled && (
                <Button variant="outline" onClick={handleMFADisable} disabled={mfaLoading}>
                  {mfaLoading ? 'Disabling...' : 'Disable MFA'}
                </Button>
              )}
            </div>

            {showMFASetup && qrCode && (
              <form onSubmit={handleMFAEnable} className="space-y-4 p-4 border rounded-lg">
                <div>
                  <p className="font-medium mb-2">Step 1: Scan QR Code</p>
                  <p className="text-sm text-gray-600 mb-3">
                    Use an authenticator app (Google Authenticator, Bitwarden, Authy, etc.)
                  </p>
                  <div className="flex justify-center p-4 bg-white rounded">
                    <img src={qrCode} alt="MFA QR Code" className="max-w-xs" />
                  </div>
                </div>

                <div>
                  <p className="font-medium mb-2">Step 2: Enter Verification Code</p>
                  <Label htmlFor="verificationCode">6-Digit Code from App</Label>
                  <Input
                    id="verificationCode"
                    type="text"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="000000"
                    required
                    minLength={6}
                    maxLength={6}
                    className="text-center text-2xl tracking-widest font-mono"
                  />
                </div>

                <div className="flex gap-2">
                  <Button type="submit" disabled={mfaLoading || verificationCode.length !== 6}>
                    {mfaLoading ? 'Verifying...' : 'Verify and Enable'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowMFASetup(false);
                      setQrCode('');
                      setMfaSecret('');
                      setVerificationCode('');
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
