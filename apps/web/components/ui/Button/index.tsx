'use client';

import { Button as DSButton } from '@valliance-ai/design-system';
import type { ComponentProps } from 'react';

type DSButtonProps = ComponentProps<typeof DSButton>;

type LocalVariant = 'primary' | 'secondary' | 'ghost';
type LocalSize = 'sm' | 'md' | 'lg';

const VARIANT_MAP: Record<LocalVariant, DSButtonProps['variant']> = {
  primary: 'default',
  secondary: 'secondary-light',
  ghost: 'ghost',
};

const SIZE_MAP: Record<LocalSize, DSButtonProps['size']> = {
  sm: 'sm',
  md: 'default',
  lg: 'lg',
};

interface ButtonProps extends Omit<DSButtonProps, 'variant' | 'size'> {
  variant?: LocalVariant;
  size?: LocalSize;
}

export default function Button({ variant = 'primary', size = 'md', ...props }: ButtonProps) {
  return <DSButton variant={VARIANT_MAP[variant]} size={SIZE_MAP[size]} {...props} />;
}
