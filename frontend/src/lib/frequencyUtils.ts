/**
 * Frequency normalization utilities for financial calculations
 */

export const FREQUENCY_MULTIPLIERS = {
  daily: 30,
  weekly: 4.33,
  fortnightly: 2.17,
  monthly: 1,
  bi_monthly: 0.5,  // Every 2 months
  quarterly: 0.333,  // Every 3 months
  semi_annually: 0.1667,  // Every 6 months
  yearly: 0.0833,
} as const;

export type FrequencyType = keyof typeof FREQUENCY_MULTIPLIERS;

/**
 * Normalize an amount to monthly equivalent
 */
export function normalizeToMonthly(
  amount: number,
  frequency: FrequencyType
): number {
  return amount * FREQUENCY_MULTIPLIERS[frequency];
}

/**
 * Format currency in Australian dollars
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
  }).format(amount);
}

/**
 * Format frequency for display
 */
export function formatFrequency(frequency: FrequencyType): string {
  const displayNames: Record<FrequencyType, string> = {
    daily: 'Daily',
    weekly: 'Weekly',
    fortnightly: 'Fortnightly',
    monthly: 'Monthly',
    bi_monthly: 'Bi-Monthly',
    quarterly: 'Quarterly',
    semi_annually: 'Semi-Annually',
    yearly: 'Yearly',
  };

  return displayNames[frequency] || frequency;
}
