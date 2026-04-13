# Notion Sync Learnings

### [2026-04-09] Always log Notion property types before mapping

**Context**: Built the BookmarkTransformer assuming "Valliance Themes" was a select and "Valliance Topics" was a multi_select. Both are actually relations. "* Theme" is the actual select field. Spent multiple iterations guessing property names and types.
**Correction**: Added diagnostic logging that dumps property type and keys on the first record. Should have done this from the start.
**Rule**: When mapping Notion properties, always log the actual property types (`prop.get("type")`) on the first record before writing extraction logic. Never assume a property type from its name. Relation properties only contain IDs, not displayable names.
**Applies to**: apps/nlp/sync/bookmark_transformer.py, apps/nlp/sync/session_transformer.py

### [2026-04-09] Notion relation properties require extra API calls to resolve names

**Context**: "Valliance Topics" and "Valliance Themes" are relation properties. Relations only return page IDs, not titles. To get names, you must call `GET /pages/{id}` for each related page.
**Correction**: Currently returning empty lists for relation properties. The next step is to implement a batch page title resolver in the Notion client, or use rollup properties if available.
**Rule**: Notion relation properties are IDs only. Either (a) add rollup columns in Notion that expose the title, or (b) batch-resolve page IDs via the Notion API. Never assume relation values contain names.
**Applies to**: apps/nlp/sync/bookmark_transformer.py, apps/nlp/sync/notion_client.py

### [2026-04-09] Actual Notion Bookmarks DB property names and types

The canonical property mapping for database `22d575346e48818ebf26d6c958efe16f`:

| Notion Property | Type | Maps to |
|---|---|---|
| Name | title | title |
| URL | url | url |
| Source | select | source |
| Topics | multi_select | topic_names |
| Valliance Topics | relation | (IDs only, not resolved) |
| Valliance Themes | relation | (IDs only, not resolved) |
| * Theme | select | theme_name (gospel) |
| * Edge/foundational | select | edge_or_foundational |
| * Focus | select | focus |
| * Time consumption | select | time_consumption |
| Summary | rich_text | ai_summary |
| Valliance viewpoint | rich_text | valliance_viewpoint |
| Date Added | date | date_added |
| Arc Bucket | multi_select | arc_bucket_names |

Other properties exist but are not currently mapped: AI Enhanced, Author, Status, Liked By, Promote for Discussion, etc.

### [2026-04-10] Discussion Recordings DB schema (NOTION_SESSIONS_DB_ID)

**Database ID**: 265575346e488076ae3dccb2eb07e42e
**Actual name**: "Discussion Recordings"

Sessions are not standalone; they are discussion recordings linked to bookmarks.
A bookmark gets a recording when its Status is "Discussed" or "Viewpoint added".

**Properties**:
| Notion Property | Type | Maps to |
|---|---|---|
| Name | title | title |
| Date Created | date | date |
| Bookmark | relation | bookmark_notion_id (first related page ID) |
| AI Suggested Viewpoint | rich_text | ai_suggested_viewpoint |

**What does NOT exist** (contrary to original module spec):
- No "Duration", "Summary", "Transcript", or "Arc" properties
- Transcript lives in the page body (block children), needs blocks API
- Arc is derived via: Recording -> Bookmark relation -> BELONGS_TO_ARC -> Arc

### [2026-04-09] session_date vs date field name mismatch

**Context**: SessionTransformer output `session_date` but the API's SessionSyncRequest model expected `date`. Sessions synced without dates, making date filtering return nothing.
**Correction**: Renamed to `date` in the transformer.
**Rule**: Always cross-reference transformer output field names against the target Pydantic model. Field name mismatches are silent — Pydantic ignores extra fields and uses defaults for missing ones.
**Applies to**: apps/nlp/sync/session_transformer.py, apps/api/models/sync.py

### [2026-04-09] Sync runner tracks last_sync timestamp — use --full for re-sync

**Context**: After fixing the transformer, only recently-edited records were re-synced because the runner checks `last_edited_time` against a stored timestamp in `sync_state.json`.
**Correction**: Added `--full` flag that clears the sync state, forcing a complete re-fetch.
**Rule**: After changing field mapping logic, always re-sync with `--full` to backfill corrected data for all records.
**Applies to**: apps/nlp/sync/runner.py, apps/nlp/sync_state.json
