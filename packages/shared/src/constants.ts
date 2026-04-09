/** Arc names indexed by arc number. */
export const ARC_NAMES: Record<number, string> = {
  1: "Agentic AI",
  2: "Palantir/Ontology",
  3: "People Enablement",
  4: "Consulting Craft",
  5: "Agentic Engineering",
  6: "Value Realisation",
} as const;

/** Proposition types. */
export const PROPOSITIONS = {
  P1: "P1",
  V1: "V1",
} as const;

export type Proposition = (typeof PROPOSITIONS)[keyof typeof PROPOSITIONS];

/** Position statuses. */
export const POSITION_STATUSES = {
  DRAFT: "draft",
  LOCKED: "locked",
  SUPERSEDED: "superseded",
} as const;

export type PositionStatus =
  (typeof POSITION_STATUSES)[keyof typeof POSITION_STATUSES];

/** Argument sentiments. */
export const ARGUMENT_SENTIMENTS = {
  SUPPORTS: "supports",
  CHALLENGES: "challenges",
  NEUTRAL: "neutral",
} as const;

export type ArgumentSentiment =
  (typeof ARGUMENT_SENTIMENTS)[keyof typeof ARGUMENT_SENTIMENTS];

/** Action item statuses. */
export const ACTION_ITEM_STATUSES = {
  OPEN: "open",
  IN_PROGRESS: "in_progress",
  DONE: "done",
} as const;

export type ActionItemStatus =
  (typeof ACTION_ITEM_STATUSES)[keyof typeof ACTION_ITEM_STATUSES];

/** Cross-arc bridge strength levels. */
export const BRIDGE_STRENGTHS = {
  CORE: "Core",
  SUPPORTING: "Supporting",
  TANGENTIAL: "Tangential",
} as const;

export type BridgeStrength =
  (typeof BRIDGE_STRENGTHS)[keyof typeof BRIDGE_STRENGTHS];

/** Neo4j relationship type constants. */
export const RELATIONSHIPS = {
  TAGGED_WITH: "TAGGED_WITH",
  HAS_THEME: "HAS_THEME",
  DISCUSSED_IN: "DISCUSSED_IN",
  EVIDENCES: "EVIDENCES",
  RELATES_TO: "RELATES_TO",
  AUTHORED_BY: "AUTHORED_BY",
  COVERS_PLAYER: "COVERS_PLAYER",
  PUBLISHED_BY: "PUBLISHED_BY",
  COVERS: "COVERS",
  PRODUCED: "PRODUCED",
  GENERATED: "GENERATED",
  REFERENCED: "REFERENCED",
  CONTAINED: "CONTAINED",
  PRESENTED_IN: "PRESENTED_IN",
  RAISED: "RAISED",
  ASSIGNED: "ASSIGNED",
  PROMOTED: "PROMOTED",
  LOCKED: "LOCKED",
  OWNS: "OWNS",
  SUPPORTS: "SUPPORTS",
  CHALLENGES: "CHALLENGES",
  REFERENCES: "REFERENCES",
  MADE_IN: "MADE_IN",
  COUNTERED_BY: "COUNTERED_BY",
  LOCKED_IN: "LOCKED_IN",
  HAS_ANTI_POSITION: "HAS_ANTI_POSITION",
  BRIDGES_TO: "BRIDGES_TO",
  MAPS_TO: "MAPS_TO",
  TESTED_BY: "TESTED_BY",
  REPLACED_BY: "REPLACED_BY",
  FOLLOWS: "FOLLOWS",
  HAS_STEELMAN: "HAS_STEELMAN",
  HAS_POSITION: "HAS_POSITION",
  CO_OCCURS_WITH: "CO_OCCURS_WITH",
  SOURCED_FROM: "SOURCED_FROM",
  GENERATED_IN: "GENERATED_IN",
} as const;
