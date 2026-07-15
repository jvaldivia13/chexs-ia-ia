import json
import logging
import os
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)
DEFAULT_GUIDELINES_PATH = Path(__file__).resolve().parent / "reasoning_guidelines.json"
MAX_ITEMS_PER_SECTION = 20
MAX_TEXT_LENGTH = 500


def load_reasoning_guidelines(profile: dict, path: Optional[Path] = None) -> dict:
    """Merge default, persona, named-agent and grandmaster-style reasoning instructions."""
    config_path = path or Path(os.getenv("CHESS_REASONING_GUIDELINES", DEFAULT_GUIDELINES_PATH))
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        logger.warning("Could not load reasoning guidelines from %s: %s", config_path, exc)
        return {"guidelines": [], "skills": [], "summary": ""}

    style_section = data.get("styles", {}).get(profile.get("style") or "", {})
    if not isinstance(style_section, dict):
        style_section = {}

    sections = [data.get("defaults", {})]
    sections.append(data.get("personas", {}).get(profile.get("persona", "balanced"), {}))
    sections.append(data.get("agents", {}).get(profile.get("name", ""), {}))
    sections.append(style_section)

    guidelines: list[str] = []
    skills: list[dict] = []
    seen_skills: set[str] = set()
    for section in sections:
        if not isinstance(section, dict):
            continue
        raw_guidelines = section.get("guidelines", [])
        raw_skills = section.get("skills", [])
        if not isinstance(raw_guidelines, list):
            raw_guidelines = []
        if not isinstance(raw_skills, list):
            raw_skills = []
        for guideline in raw_guidelines[:MAX_ITEMS_PER_SECTION]:
            if isinstance(guideline, str) and guideline.strip():
                guidelines.append(guideline.strip()[:MAX_TEXT_LENGTH])
        for skill in raw_skills[:MAX_ITEMS_PER_SECTION]:
            if not isinstance(skill, dict):
                continue
            name = skill.get("name")
            instruction = skill.get("instruction")
            if not isinstance(name, str) or not isinstance(instruction, str) or not name.strip() or not instruction.strip():
                continue
            normalized_name = name.strip()[:80]
            if normalized_name in seen_skills:
                continue
            seen_skills.add(normalized_name)
            skills.append({
                "name": normalized_name,
                "instruction": instruction.strip()[:MAX_TEXT_LENGTH],
            })

    summary = ""
    raw_summary = style_section.get("summary")
    if isinstance(raw_summary, str) and raw_summary.strip():
        summary = raw_summary.strip()[:MAX_TEXT_LENGTH]

    return {"guidelines": guidelines, "skills": skills, "summary": summary}


def format_reasoning_guidelines(profile: dict) -> str:
    reasoning = load_reasoning_guidelines(profile)
    if not reasoning["guidelines"] and not reasoning["skills"] and not reasoning["summary"]:
        return ""

    lines: list[str] = []
    if reasoning["summary"]:
        lines.append(reasoning["summary"])
    if reasoning["guidelines"] or reasoning["skills"]:
        lines.append("Reasoning guidelines configured for this agent:")
        lines.extend(f"- Guideline: {item}" for item in reasoning["guidelines"])
        lines.extend(
            f"- Skill [{skill['name']}]: {skill['instruction']}"
            for skill in reasoning["skills"]
        )
    return "\n".join(lines) + "\n"
