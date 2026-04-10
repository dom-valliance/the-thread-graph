'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { Bookmark, BookmarkEdge } from '@/types/entities';
import { getArcBookmarks, getArcBookmarkEdges } from '@/lib/api-client';

const PAGE_SIZE = 10;

interface UseArcBookmarksResult {
  bookmarks: Bookmark[];
  edges: BookmarkEdge[];
  hasMore: boolean;
  isLoading: boolean;
  loadMore: () => void;
  reset: () => void;
}

export function useArcBookmarks(arcName: string | null): UseArcBookmarksResult {
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [edges, setEdges] = useState<BookmarkEdge[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const offsetRef = useRef(0);
  const arcNameRef = useRef(arcName);

  const fetchPage = useCallback(
    async (name: string, offset: number, existingBookmarks: Bookmark[]) => {
      setIsLoading(true);
      try {
        const page = await getArcBookmarks(name, offset, PAGE_SIZE);
        const newBookmarks =
          offset === 0 ? page.data : [...existingBookmarks, ...page.data];
        setBookmarks(newBookmarks);
        setHasMore(page.meta.has_more);
        offsetRef.current = offset + page.data.length;

        // Fetch edges for all accumulated bookmarks
        const allIds = newBookmarks
          .map((b) => b.notion_id ?? b.id)
          .filter(Boolean);
        if (allIds.length >= 2) {
          const newEdges = await getArcBookmarkEdges(name, allIds);
          setEdges(newEdges);
        } else {
          setEdges([]);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    arcNameRef.current = arcName;
    if (!arcName) {
      setBookmarks([]);
      setEdges([]);
      setHasMore(false);
      offsetRef.current = 0;
      return;
    }
    fetchPage(arcName, 0, []);
  }, [arcName, fetchPage]);

  const loadMore = useCallback(() => {
    const name = arcNameRef.current;
    if (name && hasMore && !isLoading) {
      fetchPage(name, offsetRef.current, bookmarks);
    }
  }, [hasMore, isLoading, bookmarks, fetchPage]);

  const reset = useCallback(() => {
    setBookmarks([]);
    setEdges([]);
    setHasMore(false);
    offsetRef.current = 0;
  }, []);

  return { bookmarks, edges, hasMore, isLoading, loadMore, reset };
}
