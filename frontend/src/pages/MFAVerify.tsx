import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuthStore } from '@/stores/authStore';
import { apiClient } from '@/lib/api';

export default function MFAVerify() {
  const navigate = useNavigate();
  const { setUser, mfaToken } = useAuthStore();
  const [code, setCode] = useState('');
  const [trustDevice, setTrustDevice] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!mfaToken) {
      setError('No MFA token found. Please login again.');
      setIsLoading(false);
      setTimeout(() => navigate('/'), 2000);
      return;
    }

    try {
      const response: any = await apiClient.post(
        '/auth/mfa/verify',
        {
          code,
          remember_device: trustDevice,
        },
        {
          headers: {
            Authorization: `Bearer ${mfaToken}`,
          },
        }
      );

      // Set user and navigate to dashboard
      setUser(response.user);
      navigate('/dashboard');
    } catch (err: any) {
      console.error('MFA verification error:', err);
      const errorMessage = err.response?.data?.detail || 'Invalid verification code. Please try again.';
      setError(errorMessage);
      setCode('');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    // Go back to login
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            Two-Factor Authentication
          </CardTitle>
          <CardDescription className="text-center">
            Enter the 6-digit code from your authenticator app
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleVerify}>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="code">Verification Code</Label>
              <Input
                id="code"
                type="text"
                placeholder="000000"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                required
                minLength={6}
                maxLength={6}
                autoFocus
                className="text-center text-2xl tracking-widest font-mono"
              />
              <p className="text-xs text-gray-500">
                Open your authenticator app to get the code
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="trustDevice"
                checked={trustDevice}
                onChange={(e) => setTrustDevice(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <Label htmlFor="trustDevice" className="text-sm font-normal cursor-pointer">
                Trust this device for 30 days
              </Label>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              You won't need to enter a code on this device for 30 days
            </p>
          </CardContent>

          <CardFooter className="flex flex-col gap-2">
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || code.length !== 6}
            >
              {isLoading ? 'Verifying...' : 'Verify'}
            </Button>
            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={handleCancel}
            >
              Cancel
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
