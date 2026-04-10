'use client';

import { useCallback, useEffect } from 'react';
import type { Bookmark } from '@/types/entities';

interface BookmarkDetailPanelProps {
  bookmark: Bookmark | null;
  onClose: () => void;
}

export default function BookmarkDetailPanel({
  bookmark,
  onClose,
}: BookmarkDetailPanelProps) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    },
    [onClose],
  );

  useEffect(() => {
    if (!bookmark) return;
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [bookmark, handleKeyDown]);

  if (!bookmark) return null;

  return (
    <div className="absolute right-0 top-0 z-10 flex h-full w-96 flex-col border-l border-slate-200 bg-white shadow-lg transition-transform duration-200">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-slate-200 p-4">
        <h3 className="pr-4 text-lg font-semibold text-slate-900">
          {bookmark.title}
        </h3>
        <button
          onClick={onClose}
          className="shrink-0 rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          aria-label="Close panel"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Open original link */}
        {bookmark.url && (
          <a
            href={bookmark.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 rounded bg-blue-50 px-3 py-1.5 text-sm font-medium text-blue-700 hover:bg-blue-100"
          >
            Open original
            <svg
              className="h-3.5 w-3.5"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-4.5-6H18m0 0v4.5m0-4.5L10.5 13.5"
              />
            </svg>
          </a>
        )}

        {/* Source badge */}
        {bookmark.source && (
          <div>
            <span className="text-xs font-medium uppercase text-slate-400">
              Source
            </span>
            <p className="mt-0.5 text-sm text-slate-700">{bookmark.source}</p>
          </div>
        )}

        {/* Classification */}
        <div className="flex gap-3">
          {bookmark.edge_or_foundational && (
            <span
              className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
                bookmark.edge_or_foundational === 'Edge'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-green-100 text-green-800'
              }`}
            >
              {bookmark.edge_or_foundational}
            </span>
          )}
          {bookmark.focus && (
            <span className="inline-block rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
              {bookmark.focus}
            </span>
          )}
        </div>

        {/* AI Summary */}
        {bookmark.ai_summary && (
          <div>
            <span className="text-xs font-medium uppercase text-slate-400">
              AI Summary
            </span>
            <p className="mt-1 text-sm leading-relaxed text-slate-600">
              {bookmark.ai_summary}
            </p>
          </div>
        )}

        {/* Valliance Viewpoint */}
        {bookmark.valliance_viewpoint && (
          <div>
            <span className="text-xs font-medium uppercase text-slate-400">
              Valliance Viewpoint
            </span>
            <p className="mt-1 text-sm leading-relaxed text-slate-600">
              {bookmark.valliance_viewpoint}
            </p>
          </div>
        )}

        {/* Topics */}
        {bookmark.topic_names?.length > 0 && (
          <div>
            <span className="text-xs font-medium uppercase text-slate-400">
              Topics
            </span>
            <div className="mt-1 flex flex-wrap gap-1.5">
              {bookmark.topic_names.map((topic) => (
                <span
                  key={topic}
                  className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-600"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Arc buckets */}
        {bookmark.arc_bucket_names?.length > 0 && (
          <div>
            <span className="text-xs font-medium uppercase text-slate-400">
              Arcs
            </span>
            <div className="mt-1 flex flex-wrap gap-1.5">
              {bookmark.arc_bucket_names.map((arc) => (
                <span
                  key={arc}
                  className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs text-indigo-700"
                >
                  {arc}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Date added */}
        {bookmark.date_added && (
          <div>
            <span className="text-xs font-medium uppercase text-slate-400">
              Date added
            </span>
            <p className="mt-0.5 text-sm text-slate-700">
              {bookmark.date_added}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
