import { describe, it, expect } from 'vitest';
import { formatDate, truncateText, classNames } from '@/lib/utils';

describe('formatDate', () => {
  it('formats an ISO string to dd/MM/yyyy', () => {
    expect(formatDate('2024-11-25T10:00:00Z')).toBe('25/11/2024');
  });

  it('formats a Date object to dd/MM/yyyy', () => {
    expect(formatDate(new Date(2024, 0, 7))).toBe('07/01/2024');
  });

  it('pads single-digit day and month', () => {
    expect(formatDate(new Date(2023, 2, 3))).toBe('03/03/2023');
  });
});

describe('truncateText', () => {
  it('returns text unchanged when shorter than max', () => {
    expect(truncateText('short', 10)).toBe('short');
  });

  it('returns text unchanged when exactly max length', () => {
    expect(truncateText('exact', 5)).toBe('exact');
  });

  it('truncates and appends ellipsis when longer than max', () => {
    expect(truncateText('this is a long sentence', 10)).toBe('this is a...');
  });

  it('trims trailing space before ellipsis', () => {
    expect(truncateText('hello world', 6)).toBe('hello...');
  });
});

describe('classNames', () => {
  it('returns a single class', () => {
    expect(classNames('active')).toBe('active');
  });

  it('joins multiple classes with a space', () => {
    expect(classNames('flex', 'gap-2', 'p-4')).toBe('flex gap-2 p-4');
  });

  it('filters out false, null, and undefined', () => {
    expect(classNames('base', false, null, undefined, 'visible')).toBe('base visible');
  });

  it('returns empty string when called with no args', () => {
    expect(classNames()).toBe('');
  });
});
