# NLP Pipeline Learnings

### [2026-04-10] Anthropic SDK default max_retries is too low for batch workloads

**Context**: The sync runner's theme classifier hit 529 (overloaded) errors from the Anthropic API during a full bookmark sync. The `AsyncAnthropic` client was created with default `max_retries=2`, which was insufficient for transient overload conditions.
**Correction**: Set `max_retries=5` on all `AsyncAnthropic` client instantiations (runner.py and main.py). Added a 1-second `asyncio.sleep` between Notion page batches when LLM enrichment is active to pace requests.
**Rule**: Always set `max_retries=5` (minimum) on `AsyncAnthropic` clients used in batch/sync workloads. Add pacing delays (1s+) between LLM calls in loops to avoid bursting. The SDK handles exponential backoff internally, but the default retry count is too conservative for production batch jobs.
**Applies to**: apps/nlp/sync/runner.py, apps/nlp/main.py, any future Anthropic SDK usage
