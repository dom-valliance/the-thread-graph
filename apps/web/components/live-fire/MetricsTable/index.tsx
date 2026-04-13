'use client';

import type { LiveFirePositionMetric } from '@/types/entities';

export default function MetricsTable({
  metrics,
}: {
  metrics: LiveFirePositionMetric[];
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left">
            <th className="px-3 py-2 font-medium text-slate-500">Position</th>
            <th className="px-3 py-2 font-medium text-slate-500">Uses</th>
            <th className="px-3 py-2 font-medium text-slate-500">Successes</th>
            <th className="px-3 py-2 font-medium text-slate-500">Failures</th>
            <th className="px-3 py-2 font-medium text-slate-500">Success Rate</th>
            <th className="px-3 py-2 font-medium text-slate-500">Last Used</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((m) => {
            const isHighFailure =
              m.success_rate != null && m.success_rate < 0.5;
            const isNeverUsed = m.never_used;

            return (
              <tr
                key={m.position_id}
                className={`border-b border-slate-100 ${
                  isHighFailure
                    ? 'bg-red-50'
                    : isNeverUsed
                      ? 'bg-amber-50'
                      : 'hover:bg-slate-50'
                }`}
              >
                <td className="max-w-xs truncate px-3 py-2 text-slate-900">
                  {m.position_text}
                </td>
                <td className="px-3 py-2 text-slate-700">{m.total_uses}</td>
                <td className="px-3 py-2 text-green-700">{m.successes}</td>
                <td className="px-3 py-2 text-red-700">{m.failures}</td>
                <td className="px-3 py-2 text-slate-700">
                  {m.success_rate != null
                    ? `${(m.success_rate * 100).toFixed(0)}%`
                    : '—'}
                </td>
                <td className="px-3 py-2 text-slate-600">
                  {m.last_used ?? 'Never'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
