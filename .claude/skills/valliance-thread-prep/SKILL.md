---
name: valliance-thread-prep
description: >
  Prepare the weekly Valliance Thread session by pulling recent bookmarks from Notion, mapping them to the current arc's PMF canvas anchors, and producing a session prep brief. Use this skill whenever the user mentions preparing for a Thread session, prepping for Friday, pulling bookmarks for the Thread, preparing an arc, or asks what this week's Thread should cover. Also trigger when the user says things like "prep Week 3", "what are we discussing this Friday", "pull the latest for Arc 2", "get the bookmarks ready", or "simulate a Week 1". This skill is the bridge between the Bookmarks DB and the Valliance Thread curriculum.
---

# Thread Prep

This skill prepares a weekly Valliance Thread session. The Valliance Thread is a continuous 12-week learning curriculum that runs every Friday afternoon. Six arcs, two weeks each. This skill pulls recent evidence from the Notion Bookmarks DB, maps it to the current arc's PMF canvas anchors, and produces a structured session prep brief.

The output of this skill is not a presentation. It is the fuel for a structured debate. The goal is to give the lead and the team the sharpest possible evidence base for the session, grounded in what is happening right now rather than what was happening when the curriculum was written.

## When to use this skill

Use it at the start of each week (Monday or Tuesday ideally) to prepare for Friday's session. It can also be used ad hoc to check whether recent bookmarks warrant a Flash (an urgent update to a previously locked position).

## Step 1: Determine the current week

Ask the user which arc and week they are preparing for. If they are not sure, ask:
- Which arc number (1-6) or topic?
- Is it a Week 1 (Problem + Landscape) or Week 2 (Position + Pitch)?

Read `references/arc-structure.md` to look up the arc's PMF canvas anchors, questions, landscape players, and search terms.

## Step 2: Pull recent bookmarks

Search the Bookmarks DB in Notion using the arc's search terms. The data source URL is:

```
collection://22d57534-6e48-8126-8580-000be39ca605
```

Run multiple searches using different search terms from the arc definition. Cast a wide net. Filter by creation date: pull bookmarks from the past 7-14 days. If the haul is thin, extend to 21 days.

For each bookmark that looks relevant, fetch the full page to get the Valliance viewpoint, AI summary, and any content. You need enough detail to assess whether the bookmark genuinely maps to a PMF canvas anchor or is merely adjacent.

## Step 3: Map bookmarks to PMF canvas anchors

For each relevant bookmark, identify which PMF canvas anchor it addresses. The anchors for the current arc are listed in `references/arc-structure.md`. A bookmark may address more than one anchor.

Discard bookmarks that are interesting but do not map to any anchor for this arc. They may be relevant to a different arc. Note them as such but do not include them in the prep brief.

Rank the remaining bookmarks by strength of evidence. Prefer:
- Bookmarks with concrete data, case studies, or named companies over opinion pieces
- Bookmarks that expose a failure mode or gap (useful for Problem framing) over those that describe success
- Bookmarks that describe a specific player's approach (useful for Landscape mapping) over generic industry overviews
- Bookmarks with a Valliance viewpoint already written (someone on the team already thought this mattered)
- Bookmarks tagged as "Promoted For Discussion" (the team has already flagged this as worth discussing)

## Step 4: Produce the session prep brief

The output depends on the week type.

### Week 1 (Problem + Landscape) prep brief

Produce:

**1. Sharpened Problem Question**

The curriculum contains a generic problem question for each arc. Sharpen it using the specific evidence found in this week's bookmarks. The sharpened question should be answerable using the evidence at hand, not a broad philosophical prompt.

Format: State the sharpened question, then explain in 2-3 sentences why the evidence suggests this framing over the generic one.

**2. Sharpened Landscape Question**

Same treatment. Use the bookmarks to identify which players are most active or most relevant right now, and sharpen the landscape question accordingly.

**3. Bookmark-to-Anchor Mapping**

A table showing each selected bookmark, which PMF anchor it maps to, and a one-line summary of what it contributes to the session.

| Bookmark | PMF Anchor | Contribution |
|----------|-----------|-------------|
| Title (source, date) | Anchor name | What this adds to the discussion |

**4. Steelman Suggestion**

Based on the landscape evidence, propose a Steelman argument. This should be the strongest competitor case the lead could argue. It should be specific and grounded in this week's evidence, not a generic "competitor X is big."

Format: State the steelman in quotes as if the lead were delivering it, then explain in 1-2 sentences why this is the right steelman for this week.

**5. Workshop Grid Criteria**

Propose 5-7 evaluation criteria for the Landscape Map comparison grid. These should emerge naturally from the problem evidence. Each criterion should test something specific about each player's approach.

| Criterion | What it tests |
|-----------|--------------|
| Name | One-sentence description |

**6. Reading Assignments**

Assign bookmarks to team members, one player per person. State which player each person should research and which bookmark(s) are their primary reading. If you do not know the team roster, list assignments by role (Person A, Person B, etc.) and note that the lead should assign names.

**7. Adjacent Bookmarks (other arcs)**

List any bookmarks from the pull that are relevant to a different arc. Tag them with the arc they belong to. These may be useful for future prep or may warrant a Flash if they challenge a locked position.

### Week 2 (Position + Pitch) prep brief

Week 2 prep is lighter because the position is drafted by the lead, not sourced from bookmarks. The skill's job is to surface any new evidence that should inform the position or that the Ghost Prospect might raise.

Produce:

**1. New evidence since Week 1**

Any bookmarks added since the Week 1 session that are relevant to this arc. These might strengthen or challenge the emerging position.

**2. Objection fuel**

Bookmarks that a Ghost Prospect or sceptical buyer might cite to challenge the Valliance position. The lead should prepare for these.

**3. Cross-Arc Bridge prompts**

Any bookmarks that connect this arc to a previous arc's locked position. These help the lead articulate the Cross-Arc Bridge.

**4. P1/V1 signal**

Any bookmarks that speak specifically to how this arc's topic serves the People First or Value First proposition. Helps the lead prepare the P1/V1 Mapping.

## Step 5: Flash check

After mapping the bookmarks, check whether any of them challenge a previously locked position from a different arc. If so, flag it as a potential Flash with the format:

**Potential Flash:** [Bookmark title] challenges the [Arc N] position on [specific claim]. Recommend raising in Live Fire on Friday.

## Output format

Save the prep brief as a markdown file. The naming convention is:

```
Thread-Prep_Arc[N]-Week[W]_[date].md
```

Example: `Thread-Prep_Arc1-Week1_2026-03-20.md`

Save to the outputs directory under a `thread-prep` subfolder.

## Notes

- The curriculum document lives at `.claude/modules/Valliance-Thread_Curriculum_v3.md`. If the user asks about the curriculum structure or you need to check specific session details, read it directly.
- The Bookmarks DB is large. Do not try to fetch the entire database. Use targeted searches with the arc's search terms.
- If the bookmarks haul is thin for a given arc, say so. A thin haul is useful information: it may mean the team is not bookmarking enough in that area, which is worth raising.
- British English throughout.
