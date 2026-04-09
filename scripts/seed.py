"""Idempotent seed script for the Thread Graph Neo4j database.

Reads connection details from environment variables:
    NEO4J_URI      (default: bolt://localhost:7687)
    NEO4J_USER     (default: neo4j)
    NEO4J_PASSWORD (default: changeme)

All writes use MERGE with ON CREATE SET / ON MATCH SET so the script
is safe to run repeatedly without duplicating data.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

from neo4j import AsyncGraphDatabase


NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "changeme")

ARCS = [
    {"number": 1, "name": "Agentic AI"},
    {"number": 2, "name": "Palantir/Ontology"},
    {"number": 3, "name": "People Enablement"},
    {"number": 4, "name": "Consulting Craft"},
    {"number": 5, "name": "Agentic Engineering"},
    {"number": 6, "name": "Value Realisation"},
]

ARC_FOLLOWS = [
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 6),
]

PROPOSITIONS = [
    {"name": "P1"},
    {"name": "V1"},
]

PERSONS = [
    {"email": "dom@valliance.ai", "name": "Dom"},
    {"email": "team1@valliance.ai", "name": "Team Member 1"},
    {"email": "team2@valliance.ai", "name": "Team Member 2"},
]

TOPICS = [
    "AI Agents",
    "Knowledge Graphs",
    "Ontology",
    "Consulting",
    "People",
]

BOOKMARKS = [
    {
        "notion_id": "seed-bookmark-001",
        "title": "Introduction to AI Agents",
        "ai_summary": "Overview of autonomous agent architectures and their applications.",
        "date_added": "2025-01-15",
        "topics": ["AI Agents"],
    },
    {
        "notion_id": "seed-bookmark-002",
        "title": "Knowledge Graphs in Practice",
        "ai_summary": "Practical patterns for building and querying knowledge graphs.",
        "date_added": "2025-02-10",
        "topics": ["Knowledge Graphs", "Ontology"],
    },
    {
        "notion_id": "seed-bookmark-003",
        "title": "The Future of Consulting",
        "ai_summary": "How AI reshapes the consulting industry and enables new value models.",
        "date_added": "2025-03-05",
        "topics": ["Consulting", "People"],
    },
]


async def seed_arcs(session) -> None:
    """Create Arc nodes."""
    query = """
    UNWIND $arcs AS arc
    MERGE (a:Arc {number: arc.number})
        ON CREATE SET a.name = arc.name,
                      a.created_at = datetime(),
                      a.updated_at = datetime()
        ON MATCH SET  a.name = arc.name,
                      a.updated_at = datetime()
    """
    await session.run(query, arcs=ARCS)
    print(f"  Arcs: {len(ARCS)} merged")


async def seed_arc_follows(session) -> None:
    """Create FOLLOWS relationships between consecutive Arcs."""
    query = """
    UNWIND $pairs AS pair
    MATCH (from:Arc {number: pair[0]})
    MATCH (to:Arc {number: pair[1]})
    MERGE (from)-[:FOLLOWS]->(to)
    """
    await session.run(query, pairs=ARC_FOLLOWS)
    print(f"  Arc FOLLOWS: {len(ARC_FOLLOWS)} merged")


async def seed_propositions(session) -> None:
    """Create Proposition nodes."""
    query = """
    UNWIND $props AS prop
    MERGE (pr:Proposition {name: prop.name})
        ON CREATE SET pr.created_at = datetime(),
                      pr.updated_at = datetime()
        ON MATCH SET  pr.updated_at = datetime()
    """
    await session.run(query, props=PROPOSITIONS)
    print(f"  Propositions: {len(PROPOSITIONS)} merged")


async def seed_persons(session) -> None:
    """Create Person nodes."""
    query = """
    UNWIND $persons AS person
    MERGE (p:Person {email: person.email})
        ON CREATE SET p.name = person.name,
                      p.created_at = datetime(),
                      p.updated_at = datetime()
        ON MATCH SET  p.name = person.name,
                      p.updated_at = datetime()
    """
    await session.run(query, persons=PERSONS)
    print(f"  Persons: {len(PERSONS)} merged")


async def seed_topics(session) -> None:
    """Create Topic nodes."""
    query = """
    UNWIND $topics AS topic_name
    MERGE (t:Topic {name: topic_name})
        ON CREATE SET t.created_at = datetime(),
                      t.updated_at = datetime()
        ON MATCH SET  t.updated_at = datetime()
    """
    await session.run(query, topics=TOPICS)
    print(f"  Topics: {len(TOPICS)} merged")


async def seed_bookmarks(session) -> None:
    """Create Bookmark nodes and TAGGED_WITH relationships to Topics."""
    for bm in BOOKMARKS:
        query = """
        MERGE (b:Bookmark {notion_id: $notion_id})
            ON CREATE SET b.title = $title,
                          b.ai_summary = $ai_summary,
                          b.date_added = date($date_added),
                          b.created_at = datetime(),
                          b.updated_at = datetime()
            ON MATCH SET  b.title = $title,
                          b.ai_summary = $ai_summary,
                          b.date_added = date($date_added),
                          b.updated_at = datetime()
        WITH b
        UNWIND $topics AS topic_name
        MATCH (t:Topic {name: topic_name})
        MERGE (b)-[:TAGGED_WITH]->(t)
        """
        await session.run(
            query,
            notion_id=bm["notion_id"],
            title=bm["title"],
            ai_summary=bm["ai_summary"],
            date_added=bm["date_added"],
            topics=bm["topics"],
        )
    print(f"  Bookmarks: {len(BOOKMARKS)} merged (with TAGGED_WITH relationships)")


async def main() -> None:
    print(f"Connecting to Neo4j at {NEO4J_URI} as {NEO4J_USER}")
    driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    try:
        await driver.verify_connectivity()
        print("Connected successfully.\n")

        print("Seeding data...")
        async with driver.session() as session:
            await seed_arcs(session)
            await seed_arc_follows(session)
            await seed_propositions(session)
            await seed_persons(session)
            await seed_topics(session)
            await seed_bookmarks(session)

        print("\nSeed complete.")
    finally:
        await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
