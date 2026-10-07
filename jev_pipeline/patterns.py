"""Question templates used by the `draft` step.

Condensed from the CC0 pattern library awesome-jev-prompts
(https://github.com/vicfei/awesome-jev-prompts) — each template keeps the
library's rules: atomic judgment, an escape option for Choice, an ordered
rubric for Score, variable content passed via state.
"""

from __future__ import annotations

PATTERNS: dict[str, dict] = {
    "intent-routing": {
        "primitive": "choice",
        "keywords": ["classify", "class", "category", "label", "route", "routing", "intent", "triage", "queue"],
        "question": {
            "kind": "Choice",
            "instructions": "What is the primary intent of the input?",
            "criteria": {
                "action_needed": "The sender asks for something concrete to be done.",
                "information": "The sender only asks for information.",
                "spam_promo": "Unsolicited marketing or spam.",
                "other": "None of the above clearly fits.",
            },
        },
        "source": "categories/choice-patterns.md#intent-routing",
    },
    "tool-selection": {
        "primitive": "choice",
        "keywords": ["tool", "agent", "skill", "which", "dispatch", "pick"],
        "question": {
            "kind": "Choice",
            "instructions": "Which tool should handle the current step?",
            "criteria": {
                "search": "The step needs search over code or text.",
                "edit": "The step is a concrete edit with a known target.",
                "run": "The step needs a command or test execution.",
                "none": "No tool is needed; answer directly.",
            },
        },
        "source": "categories/choice-patterns.md#tool-selection-for-agents",
    },
    "severity-rubric": {
        "primitive": "score",
        "keywords": ["severity", "priority", "urgent", "escalate", "incident", "sla"],
        "question": {
            "kind": "Score",
            "instructions": "How severe is this report?",
            "criteria": [
                "Cosmetic or informational; no functional impact.",
                "Minor impairment; a workaround exists.",
                "Major function broken for some users.",
                "Outage or data loss; urgent response required.",
            ],
        },
        "source": "categories/score-patterns.md#severity-rubric",
    },
    "quality-gate": {
        "primitive": "score",
        "keywords": ["review", "quality", "gate", "merge", "approve", "verdict"],
        "question": {
            "kind": "Score",
            "instructions": "Rate the produced work against the task requirements.",
            "criteria": [
                "Wrong: does not address the task.",
                "Partial: addresses the task with clear defects.",
                "Acceptable: meets requirements with minor issues.",
                "Excellent: meets requirements and is robust.",
            ],
        },
        "source": "categories/score-patterns.md#quality-gate",
    },
    "policy-check": {
        "primitive": "noul",
        "keywords": ["policy", "safe", "safety", "violate", "block", "allow", "guard", "ban"],
        "question": {
            "kind": "Noul",
            "instructions": "Does the input violate the stated policy?",
        },
        "source": "categories/noul-patterns.md#policy-violation-check",
    },
    "duplicate-check": {
        "primitive": "noul",
        "keywords": ["duplicate", "dedup", "same", "match", "identity", "entity"],
        "question": {
            "kind": "Noul",
            "instructions": "Do these two items refer to the same underlying entity?",
        },
        "source": "categories/noul-patterns.md#duplicate-detection",
    },
    "keep-or-drop": {
        "primitive": "score",
        "keywords": ["context", "memory", "compact", "keep", "prune", "history"],
        "question": {
            "kind": "Score",
            "instructions": "How much will this item matter for the remaining task?",
            "criteria": [
                "Noise: greetings, boilerplate, spent tool output.",
                "Maybe: context that could matter.",
                "Likely: decisions and constraints already established.",
                "Critical: the task goal, key facts, or blocking state.",
            ],
        },
        "source": "categories/context-compaction.md#keep-or-drop-for-messages",
    },
    "escalation-trigger": {
        "primitive": "noul",
        "keywords": ["escalate", "human", "uncertain", "confidence", "review"],
        "question": {
            "kind": "Noul",
            "instructions": "Does this situation need a human decision before we act?",
        },
        "source": "categories/noul-patterns.md#human-escalation-trigger",
    },
}

_PRIMITIVE_FALLBACK = {"choice": "intent-routing", "score": "severity-rubric", "noul": "policy-check"}


def draft_for(primitive: str, decision_text: str) -> tuple[str, dict]:
    """Pick the best pattern for a decision, by keyword overlap then primitive."""
    text = decision_text.lower()
    best, best_hits = None, 0
    for pid, pat in PATTERNS.items():
        hits = sum(1 for k in pat["keywords"] if k in text)
        if hits > best_hits:
            best, best_hits = pid, hits
    if best is None:
        best = _PRIMITIVE_FALLBACK.get(primitive, "intent-routing")
    return best, PATTERNS[best]["question"]
