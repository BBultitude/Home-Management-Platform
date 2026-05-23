import { Calendar as CalendarIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

type FinancialYearPickerProps = Readonly<{
  value?: string; // Format: "2024-2025"
  onChange: (value: string) => void;
  yearsBack?: number; // How many years back to show
  yearsForward?: number; // How many years forward to show
  disabled?: boolean;
  className?: string;
}>

/**
 * Gets the current Australian financial year in format "2024-2025"
 * FY runs from July 1 to June 30
 */
export function getCurrentFinancialYear(): string {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth(); // 0-indexed

  // If we're before July (month 6), we're still in the previous FY
  if (currentMonth < 6) {
    return `${currentYear - 1}-${currentYear}`;
  }
  return `${currentYear}-${currentYear + 1}`;
}

/**
 * Generates a list of financial years
 */
function generateFinancialYears(yearsBack: number, yearsForward: number): string[] {
  const current = getCurrentFinancialYear();
  const [currentStart] = current.split('-').map(Number);

  const years: string[] = [];
  for (let i = -yearsBack; i <= yearsForward; i++) {
    const startYear = currentStart + i;
    years.push(`${startYear}-${startYear + 1}`);
  }

  return years;
}

export function FinancialYearPicker({
  value,
  onChange,
  yearsBack = 5,
  yearsForward = 1,
  disabled = false,
  className,
}: FinancialYearPickerProps) {
  const financialYears = generateFinancialYears(yearsBack, yearsForward);
  const currentFY = getCurrentFinancialYear();

  return (
    <Select value={value || currentFY} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger className={cn('w-full', className)}>
        <CalendarIcon className="mr-2 h-4 w-4" />
        <SelectValue placeholder="Select financial year" />
      </SelectTrigger>
      <SelectContent>
        {financialYears.map((fy) => (
          <SelectItem key={fy} value={fy}>
            FY {fy} {fy === currentFY && '(Current)'}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
