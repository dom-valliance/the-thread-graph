# Module: Notion Sync Service

Service responsible for pulling data from the two Notion databases (Bookmarks and Learning Sessions) and upserting it into the graph via the FastAPI middleware.

---

## Technology

- Python 3.12
- httpx (async HTTP client for Notion API)
- Pydantic v2 (Notion response parsing, transformation)
- Runs as part of the NLP pipeline app or as a standalone script

## Responsibilities

- Poll Notion Bookmarks DB for new and updated entries.
- Poll Notion Learning Sessions DB for new and updated entries.
- Transform Notion page properties into graph-compatible models.
- Upsert bookmarks and sessions via FastAPI sync endpoints.
- Track last-sync timestamp per database to enable incremental sync.
- Handle Notion API rate limits (3 req/s) with backoff.

## Directory Structure

```
apps/api/services/
├── notion_sync_service.py      # Orchestration: poll, transform, submit

apps/nlp/                       # Or standalone in scripts/
├── sync/
│   ├── notion_client.py        # Notion API wrapper with rate limiting
│   ├── bookmark_transformer.py # Notion page → BookmarkCreate model
│   ├── session_transformer.py  # Notion page → SessionCreate model
│   ├── sync_state.py           # Track last_edited_time per DB
│   └── runner.py               # Entry point for sync job
```

## Notion API Integration

### Database Queries

```python
# Bookmarks DB: fetch pages updated since last sync
POST https://api.notion.com/v1/databases/{bookmarks_db_id}/query
{
  "filter": {
    "timestamp": "last_edited_time",
    "last_edited_time": {
      "after": "<last_sync_timestamp>"
    }
  },
  "sorts": [
    { "timestamp": "last_edited_time", "direction": "ascending" }
  ],
  "page_size": 100
}
```

### Property Mapping: Bookmarks

| Notion Property | Type | Graph Field |
|----------------|------|-------------|
| Name | title | title |
| Source | rich_text | source |
| URL | url | url |
| AI Summary | rich_text | ai_summary |
| Valliance Viewpoint | rich_text | valliance_viewpoint |
| Edge or Foundational | select | edge_or_foundational |
| Focus | select | focus |
| Time Consumption | rich_text | time_consumption |
| Date Added | date | date_added |
| Topics | multi_select | topic_names[] |
| Theme | select | theme_name |

### Property Mapping: Sessions

| Notion Property | Type | Graph Field |
|----------------|------|-------------|
| Name | title | title |
| Date | date | date |
| Duration | number | duration |
| Summary | rich_text | summary |
| Transcript | rich_text / file | transcript |
| Arc | select | arc_focus |

## Transformer Pattern

```python
class BookmarkTransformer:
    def transform(self, notion_page: dict) -> BookmarkCreate:
        """
        Extract properties from Notion page response.
        Handle missing optional fields gracefully.
        Map multi-select Topics to list of topic name strings.
        Map select Theme to single theme name string.
        """
        props = notion_page["properties"]
        return BookmarkCreate(
            notion_id=notion_page["id"],
            title=self._extract_title(props["Name"]),
            source=self._extract_rich_text(props.get("Source")),
            url=self._extract_url(props.get("URL")),
            ai_summary=self._extract_rich_text(props.get("AI Summary")),
            valliance_viewpoint=self._extract_rich_text(props.get("Valliance Viewpoint")),
            edge_or_foundational=self._extract_select(props.get("Edge or Foundational")),
            focus=self._extract_select(props.get("Focus")),
            time_consumption=self._extract_rich_text(props.get("Time Consumption")),
            date_added=self._extract_date(props.get("Date Added")),
            topic_names=self._extract_multi_select(props.get("Topics")),
            theme_name=self._extract_select(props.get("Theme")),
        )
```

## Sync State

Track per-database sync state to enable incremental polling:

```python
class SyncState:
    """
    Persisted to a local JSON file or a dedicated graph node.
    Contains last_edited_time per Notion database ID.
    """
    def get_last_sync(self, db_id: str) -> datetime | None: ...
    def update_last_sync(self, db_id: str, timestamp: datetime) -> None: ...
```

For production, sync state is stored as a graph node:

```cypher
MERGE (s:SyncState {database_id: $db_id})
SET s.last_sync = datetime($timestamp), s.updated_at = datetime()
```

## Rate Limiting

Notion API limit: 3 requests per second, average.

```python
class RateLimitedNotionClient:
    """
    Wraps httpx.AsyncClient with:
    - Token bucket rate limiter (3 req/s)
    - Retry on 429 with Retry-After header
    - Exponential backoff: 1s, 2s, 4s, max 3 retries
    """
```

## Incremental Sync Flow

```
1. Read sync state for Bookmarks DB → last_sync_time
2. Query Notion Bookmarks DB for pages edited after last_sync_time
3. Paginate through all results (100 per page)
4. Transform each page → BookmarkCreate model
5. Batch POST to /api/v1/sync/bookmarks (50 per batch)
6. Update sync state with latest last_edited_time from results
7. Repeat steps 1-6 for Learning Sessions DB
```

## Error Handling

- Notion API errors: retry with backoff on 429 and 5xx. Log and skip individual pages on 400.
- Transform errors: log malformed pages, continue processing rest of batch.
- API submission errors: retry batch on 5xx. Log and flag individual records on 4xx.
- Full sync failure: do not update sync state; next run retries from same point.

## Testing

- **Unit**: Mock Notion API responses with fixture JSON. Test transformers produce correct models. Test rate limiter behaviour.
- **Integration**: Test full sync flow against mock Notion API and real FastAPI + Neo4j (testcontainers).
- **Fixtures**: Real Notion API response samples (anonymised if needed) in `tests/fixtures/`.

## Build and Dev

```bash
# Run full sync
python -m sync.runner

# Run bookmarks only
python -m sync.runner --db bookmarks

# Run sessions only
python -m sync.runner --db sessions

# Dry run (fetch and transform, do not submit)
python -m sync.runner --dry-run
```

## Future: Webhooks

When volume grows beyond hourly polling:

1. Register Notion webhook on both databases.
2. Webhook handler in FastAPI receives page ID.
3. Fetch individual page, transform, upsert.
4. Eliminates polling latency; real-time sync within seconds.

Not needed for Phase 1-2. Polling is sufficient for the current volume.
