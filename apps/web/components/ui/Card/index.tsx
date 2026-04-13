import {
  Card as DSCard,
  CardHeader,
  CardTitle,
  CardContent,
} from '@valliance-ai/design-system';
import type { ReactNode } from 'react';

interface CardProps {
  title?: string;
  children: ReactNode;
  className?: string;
  padding?: boolean;
}

export default function Card({ title, children, className, padding = true }: CardProps) {
  return (
    <DSCard className={className}>
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent className={padding ? undefined : 'p-0'}>{children}</CardContent>
    </DSCard>
  );
}
