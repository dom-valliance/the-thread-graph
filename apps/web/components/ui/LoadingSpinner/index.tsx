import { classNames } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const SIZE_CLASSES = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-3',
} as const;

export default function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  return (
    <div
      className={classNames(
        'animate-spin rounded-full border-slate-300 border-t-slate-900',
        SIZE_CLASSES[size],
        className,
      )}
      role="status"
      aria-label="Loading"
    />
  );
}
