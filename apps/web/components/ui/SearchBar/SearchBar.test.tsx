import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SearchBar from './index';

describe('SearchBar', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders with placeholder text', () => {
    render(<SearchBar value="" onChange={vi.fn()} placeholder="Find something" />);
    expect(screen.getByPlaceholderText('Find something')).toBeDefined();
  });

  it('calls onChange after debounce period', () => {
    const handleChange = vi.fn();
    render(<SearchBar value="" onChange={handleChange} debounceMs={300} />);

    const input = screen.getByPlaceholderText('Search...');
    fireEvent.change(input, { target: { value: 'hello' } });

    vi.advanceTimersByTime(300);

    expect(handleChange).toHaveBeenCalledOnce();
    expect(handleChange).toHaveBeenCalledWith('hello');
  });

  it('does not call onChange before debounce period elapses', () => {
    const handleChange = vi.fn();
    render(<SearchBar value="" onChange={handleChange} debounceMs={300} />);

    const input = screen.getByPlaceholderText('Search...');
    fireEvent.change(input, { target: { value: 'hello' } });

    vi.advanceTimersByTime(200);

    expect(handleChange).not.toHaveBeenCalled();
  });

  it('updates local value immediately on typing', () => {
    render(<SearchBar value="" onChange={vi.fn()} />);

    const input = screen.getByPlaceholderText('Search...') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'typed' } });

    expect(input.value).toBe('typed');
  });

  it('syncs local value when external value prop changes', () => {
    const { rerender } = render(<SearchBar value="initial" onChange={vi.fn()} />);

    const input = screen.getByPlaceholderText('Search...') as HTMLInputElement;
    expect(input.value).toBe('initial');

    rerender(<SearchBar value="updated" onChange={vi.fn()} />);

    expect(input.value).toBe('updated');
  });
});
