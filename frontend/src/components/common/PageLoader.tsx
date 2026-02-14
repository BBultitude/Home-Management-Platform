import { Spinner } from '@/components/ui/spinner';

interface PageLoaderProps {
  message?: string;
}

export function PageLoader({ message = 'Loading...' }: PageLoaderProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
      <Spinner size="lg" />
      <p className="text-sm text-gray-600">{message}</p>
    </div>
  );
}
