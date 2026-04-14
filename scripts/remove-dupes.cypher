// Rename the two canonical arcs to the preferred spellings
MATCH (a:Arc {number: 2}) SET a.name = "Palantir / Ontology", a.updated_at = datetime();
MATCH (a:Arc {number: 4}) SET a.name = "The Consulting Craft", a.updated_at = datetime();

// Move bookmarks from the orphan "Palantir / Ontology" (number IS NULL) to Arc 2
MATCH (b:Bookmark)-[r:BELONGS_TO_ARC]->(orphan:Arc {name: "Palantir / Ontology"})
WHERE orphan.number IS NULL
MATCH (canonical:Arc {number: 2})
MERGE (b)-[:BELONGS_TO_ARC]->(canonical)
DELETE r;

// Move bookmarks from the orphan "The Consulting Craft" (number IS NULL) to Arc 4
MATCH (b:Bookmark)-[r:BELONGS_TO_ARC]->(orphan:Arc {name: "The Consulting Craft"})
WHERE orphan.number IS NULL
MATCH (canonical:Arc {number: 4})
MERGE (b)-[:BELONGS_TO_ARC]->(canonical)
DELETE r;

// Verify no orphans remain with these names
MATCH (orphan:Arc) WHERE orphan.number IS NULL
  AND orphan.name IN ["The Consulting Craft", "Palantir / Ontology"]
DETACH DELETE orphan;

// Sanity check
MATCH (a:Arc)
OPTIONAL MATCH (b:Bookmark)-[:BELONGS_TO_ARC]->(a)
RETURN a.number, a.name, count(b) AS bookmark_count
ORDER BY a.number;
