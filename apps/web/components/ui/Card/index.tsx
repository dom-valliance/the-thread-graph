import type { ReactNode } from 'react';
import { classNames } from '@/lib/utils';

interface CardProps {
  title?: string;
  children: ReactNode;
  className?: string;
  padding?: boolean;
}

export default function Card({ title, children, className, padding = true }: CardProps) {
  return (
    <div
      className={classNames(
        'rounded-lg border border-slate-200 bg-white shadow-sm',
        padding && 'p-6',
        className,
      )}
    >
      {title && <h3 className="mb-4 text-base font-semibold text-slate-900">{title}</h3>}
      {children}
    </div>
  );
}
