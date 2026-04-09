'use client';

import { useCallback, useRef, useState } from 'react';

interface ContainerSize {
  width: number;
  height: number;
}

export function useContainerSize<T extends HTMLElement = HTMLDivElement>(): [
  (node: T | null) => void,
  ContainerSize,
] {
  const observerRef = useRef<ResizeObserver | null>(null);
  const [size, setSize] = useState<ContainerSize>({ width: 0, height: 0 });

  const callbackRef = useCallback((node: T | null) => {
    if (observerRef.current) {
      observerRef.current.disconnect();
      observerRef.current = null;
    }

    if (!node) return;

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (!entry) return;
      const { width, height } = entry.contentRect;
      setSize((prev) => {
        if (prev.width === Math.round(width) && prev.height === Math.round(height)) return prev;
        return { width: Math.round(width), height: Math.round(height) };
      });
    });

    observer.observe(node);
    observerRef.current = observer;
  }, []);

  return [callbackRef, size];
}
