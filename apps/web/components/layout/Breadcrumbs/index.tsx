import Link from 'next/link';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export default function Breadcrumbs({ items }: BreadcrumbsProps) {
  return (
    <nav aria-label="Breadcrumb" className="mb-4">
      <ol className="flex items-center space-x-2 text-sm text-slate-500">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li key={item.label} className="flex items-center">
              {index > 0 && <span className="mx-2 text-slate-300">/</span>}
              {item.href && !isLast ? (
                <Link href={item.href} className="hover:text-slate-700 hover:underline">
                  {item.label}
                </Link>
              ) : (
                <span className={isLast ? 'font-medium text-slate-900' : ''}>{item.label}</span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
