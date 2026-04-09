/**
 * Format a date string or Date object to British format (dd/MM/yyyy).
 */
export function formatDate(input: string | Date): string {
  const date = typeof input === 'string' ? new Date(input) : input;
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
}

/**
 * Truncate text to a maximum length, appending an ellipsis if truncated.
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength).trimEnd()}...`;
}

/**
 * Merge CSS class names, filtering out falsy values.
 */
export function classNames(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(' ');
}
