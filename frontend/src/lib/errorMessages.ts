/**
 * Maps backend error codes and messages to user-friendly messages
 */

interface ApiError {
  response?: {
    status?: number;
    data?: {
      detail?: string | Array<{ msg?: string; message?: string; loc?: string[] }>;
    };
  };
  message?: string;
}

export function getErrorMessage(error: unknown): string {
  // Type guard for API errors
  const apiError = error as ApiError;

  // Network errors
  if (!apiError.response) {
    return 'Network error. Please check your connection and try again.';
  }

  const status = apiError.response.status;
  const detail = apiError.response.data?.detail;

  // Handle Pydantic validation errors (array format)
  if (Array.isArray(detail)) {
    const messages = detail
      .map((err) => {
        const field = err.loc?.slice(-1)[0] || 'field';
        const message = err.msg || err.message || 'Invalid value';
        return `${field}: ${message}`;
      })
      .join('; ');
    return messages || 'Validation error. Please check your input.';
  }

  // Handle string error messages
  if (typeof detail === 'string') {
    // Map common backend messages to user-friendly ones
    const errorMap: Record<string, string> = {
      'Invalid credentials': 'Incorrect username or password.',
      'User not found': 'User account not found.',
      'User already exists': 'An account with this username or email already exists.',
      'Invalid MFA code': 'Incorrect verification code. Please try again.',
      'Incorrect password': 'Current password is incorrect.',
      'Token has expired': 'Your session has expired. Please log in again.',
      'Permission denied': 'You do not have permission to perform this action.',
      'Not authenticated': 'Please log in to continue.',
      'MFA required': 'Two-factor authentication is required.',
    };

    return errorMap[detail] || detail;
  }

  // Handle by status code
  const statusMessages: Record<number, string> = {
    400: 'Invalid request. Please check your input and try again.',
    401: 'Authentication required. Please log in.',
    403: 'Access denied. You do not have permission to perform this action.',
    404: 'Resource not found.',
    409: 'Conflict. This resource already exists or cannot be modified.',
    422: 'Validation error. Please check your input.',
    429: 'Too many requests. Please try again later.',
    500: 'Server error. Please try again later.',
    503: 'Service unavailable. Please try again later.',
  };

  return (status && statusMessages[status]) || 'An unexpected error occurred. Please try again.';
}

/**
 * Formats field validation errors for display
 */
export function formatValidationErrors(errors: unknown): string[] {
  if (!Array.isArray(errors)) return [];

  return errors.map((err) => {
    const field = err.loc?.slice(-1)[0] || 'Field';
    const message = err.msg || err.message || 'Invalid value';
    return `${field}: ${message}`;
  });
}
