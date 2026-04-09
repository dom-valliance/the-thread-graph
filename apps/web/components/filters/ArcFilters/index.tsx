'use client';

import Button from '@/components/ui/Button';
import { classNames } from '@/lib/utils';

const PROPOSITIONS = ['P1', 'V1'] as const;
type Proposition = (typeof PROPOSITIONS)[number];

interface ArcFiltersProps {
  activeProposition: Proposition | null;
  onToggle: (proposition: Proposition | null) => void;
}

export default function ArcFilters({ activeProposition, onToggle }: ArcFiltersProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium text-slate-600">Filter by proposition:</span>
      {PROPOSITIONS.map((prop) => (
        <Button
          key={prop}
          variant={activeProposition === prop ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => onToggle(activeProposition === prop ? null : prop)}
          className={classNames(
            activeProposition === prop && 'ring-2 ring-slate-500 ring-offset-1',
          )}
        >
          {prop}
        </Button>
      ))}
    </div>
  );
}
