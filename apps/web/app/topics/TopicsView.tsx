'use client';

import { useRouter } from 'next/navigation';
import type { Topic, TopicCoOccurrence } from '@/types/entities';
import TopicGalaxy from '@/components/graph/TopicGalaxy';

interface TopicsViewProps {
  topics: Topic[];
  coOccurrences: TopicCoOccurrence[];
}

export default function TopicsView({ topics, coOccurrences }: TopicsViewProps) {
  const router = useRouter();

  return (
    <TopicGalaxy
      topics={topics}
      coOccurrences={coOccurrences}
      onTopicSelect={(topic) => {
        router.push(`/topics/${encodeURIComponent(topic.name)}`);
      }}
    />
  );
}
