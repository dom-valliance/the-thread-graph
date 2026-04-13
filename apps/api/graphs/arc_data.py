"""Arc structure reference data.

Derived from .claude/skills/valliance-thread-prep/references/arc-structure.md.
Moved here from services/thread_prep_generator.py for reuse by the LangGraph prep graph.
"""

from __future__ import annotations

ARC_DATA: dict[int, dict[str, object]] = {
    1: {
        "name": "Agentic AI",
        "focus": "Why enterprises fail at agentic deployment. What Valliance believes about building AI that works.",
        "pmf_anchors_problem": [
            "AI Inflection Point (business model transformation)",
            "Governance & Visibility (human-agent control gap)",
            "Business Logic Layer (hidden enterprise rules)",
        ],
        "pmf_anchors_solution": [
            "Build AI That Works",
            "Holistic Enterprise Transformation (agentic systems pillar)",
            "AI Enabled Value Acceleration",
        ],
        "week1_problem_q": "Why do enterprise agentic AI deployments fail, and what are the structural reasons beyond \"it's early\"?",
        "week1_landscape_q": "How are Palantir, Anthropic, OpenAI, AWS, and the traditional SIs each approaching agentic AI, and where does each model break down?",
        "week2_position_q": "What does Valliance specifically believe about building agentic AI in the enterprise, and why should a CTO trust us over the alternatives?",
        "landscape_players": [
            "Palantir AIP", "Anthropic (Claude/MCP/Cowork)", "OpenAI (Codex/Assistants)",
            "AWS (Bedrock Agents)", "Traditional SIs (Accenture, Deloitte)",
            "DIY/open-source (LangGraph, LangChain)",
        ],
    },
    2: {
        "name": "Palantir / Ontology",
        "focus": "Why business logic is the hidden layer. What Valliance brings to ontology-led transformation.",
        "pmf_anchors_problem": [
            "Business Logic Layer (hidden enterprise rules)",
            "AI Inflection Point (need for ontological coherence)",
        ],
        "pmf_anchors_solution": [
            "Holistic Enterprise Transformation (enterprise ontology/twin pillar)",
            "Build AI That Works (data platforms, ontologies)",
        ],
        "week1_problem_q": "Why is the business logic layer the hidden bottleneck in enterprise AI, and why do most organisations not even know it exists?",
        "week1_landscape_q": "How does Palantir's ontology-first approach compare to knowledge graphs, data fabrics, semantic layers, RAG, and \"build it ourselves\"?",
        "week2_position_q": "What is Valliance's position on ontology-led enterprise AI, how does our Palantir partnership fit, and what do we bring that Palantir alone does not?",
        "landscape_players": [
            "Palantir Foundry", "Neo4j/graph databases", "Databricks Unity Catalog",
            "Informatica", "dbt/semantic layers", "RAG-only approaches",
            "Internal shadow AI teams",
        ],
    },
    3: {
        "name": "People Enablement",
        "focus": "Why adoption fails at the people layer. What Valliance believes about building capability, not compliance.",
        "pmf_anchors_problem": [
            "AI Inflection Point (enterprises that become AI-native need people transformation)",
            "Governance & Visibility (human-agent collaboration requires new skills)",
        ],
        "pmf_anchors_solution": [
            "People Lead / AI Enablement",
            "Scale The Impact (change, education/enablement)",
            "Set The Goal (education, vision, conviction)",
        ],
        "week1_problem_q": "Why does enterprise AI adoption fail at the people layer, and why is \"training\" the wrong word for what's needed?",
        "week1_landscape_q": "How are enterprises, consultancies, and technology vendors approaching AI enablement today, and why do most programmes fail to change behaviour?",
        "week2_position_q": "What does Valliance believe about people-led AI enablement, and how does our approach produce capability rather than compliance?",
        "landscape_players": [
            "Microsoft Copilot adoption programme", "Accenture change management",
            "McKinsey AI enablement", "Google Gemini Enterprise",
            "LinkedIn Learning", "Internal AI champions networks",
        ],
    },
    4: {
        "name": "The Consulting Craft",
        "focus": "Why the traditional consulting model is broken. What it means to be a Valliance consultant.",
        "pmf_anchors_problem": [],
        "pmf_anchors_solution": [
            "Value-Aligned Commercial Model (outcome-based pricing)",
            "New Consulting Model for the Future Enterprise",
            "AI Enabled Value Acceleration (value loops)",
        ],
        "week1_problem_q": "Why is the traditional consulting model broken in the age of AI, and what specific behaviours does it produce that damage client outcomes?",
        "week1_landscape_q": "How are different consulting models evolving in response to AI, and what are the emerging commercial structures that could replace time-and-materials?",
        "week2_position_q": "What does it mean to be a Valliance consultant, and how does our commercial model create better outcomes than the alternatives?",
        "landscape_players": [
            "Accenture/Deloitte (traditional SI)", "Operand/boutique AI consultancies",
            "OpenAI consulting arm", "AWS Professional Services",
            "WPP (outcome-based pivot)",
        ],
    },
    5: {
        "name": "Agentic Engineering",
        "focus": "How to build in the new world. The practitioner layer: architectures, tooling, evaluation, delivery.",
        "pmf_anchors_problem": [],
        "pmf_anchors_solution": [],
        "week1_problem_q": "What are the hardest unsolved problems in building production-grade agentic systems for the enterprise, and where does the current tooling fall short?",
        "week1_landscape_q": "What are the emerging architecture patterns, frameworks, and toolchains for building enterprise agentic systems?",
        "week2_position_q": "How does Valliance engineer agentic systems, and what are our non-negotiable technical principles for enterprise-grade builds?",
        "landscape_players": [
            "Palantir AIP/Foundry", "Anthropic Claude/MCP", "OpenAI Codex/Assistants",
            "LangGraph/LangChain", "AWS Bedrock Agents",
            "Azure AI Agent Service", "Custom architectures",
        ],
    },
    6: {
        "name": "Value Realisation",
        "focus": "How to prove and sustain AI value. Making the outcome-based model work in practice.",
        "pmf_anchors_problem": [],
        "pmf_anchors_solution": [
            "Scale The Impact (value realisation, AI ops, governance)",
            "Value-Aligned Commercial Model (ROI measurement, outcome-linked pricing)",
            "AI Enabled Value Acceleration (compound learning across cycles)",
        ],
        "week1_problem_q": "Why do most enterprises struggle to prove AI ROI, and why is the measurement problem harder than it looks?",
        "week1_landscape_q": "How are enterprises, consultancies, and vendors currently measuring and proving AI value, and where does each approach break down?",
        "week2_position_q": "How does Valliance measure and prove AI value, and how does our value loop model create a structurally better answer than the alternatives?",
        "landscape_players": [
            "McKinsey value driver trees", "Accenture value engineering",
            "Microsoft Copilot Dashboard", "Palantir value engineering",
            "Emerging AI-native measurement approaches",
        ],
    },
}
