# Neo4j Learnings

### [2026-04-13] Use OPTIONAL MATCH for cross-entity links inside multi-row UNWIND writes

**Context**: `CycleRepository.create_cycle` did `UNWIND $sessions ... MERGE (s:ScheduledSession ...) ... MATCH (a:Arc {number: ss.arc_number})`. When Arc nodes were not seeded, the inner `MATCH` dropped every row from the pipeline. The session nodes had already been MERGEd, but the `MERGE (s)-[:COVERS]->(a)` line never ran for any of them. The query returned the cycle successfully, hiding the failure. Later, `GET /cycles/{id}/schedule` projected `arc_name: a.name` and got `None`, which broke Pydantic validation on `ScheduledSessionResponse.arc_name: str`.
**Correction**: Switched to `OPTIONAL MATCH (a:Arc {number: ss.arc_number})` followed by `FOREACH (_ IN CASE WHEN a IS NOT NULL THEN [1] ELSE [] END | MERGE (s)-[:COVERS]->(a))`. Made `arc_name` nullable in the response model so missing arcs surface as null rather than a 500.
**Rule**: Inside a multi-row write (UNWIND or per-row WITH chains), never use bare `MATCH` to look up a related entity that may not exist. A failed `MATCH` silently drops the row from the rest of the pipeline, which can leave the primary write half-finished. Use `OPTIONAL MATCH` plus a `FOREACH` guard for the dependent relationship. Make any field that derives from a potentially-missing related entity nullable in the response model.
**Applies to**: apps/api/repositories/*.py, any Cypher write that links a primary entity to a lookup entity within an UNWIND
