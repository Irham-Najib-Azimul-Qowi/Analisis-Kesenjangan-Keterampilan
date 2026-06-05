"""Utilitas ekstraksi dan penilaian skill."""
import re
import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def load_skill_taxonomy(path: str) -> Dict[str, List[str]]:
    """Muat kamus skill dari file JSON."""
    with open(path, "r") as f:
        return json.load(f)


def build_flat_skills(taxonomy: Dict[str, List[str]]) -> Dict[str, str]:
    """Konversi taxonomy berhierarki menjadi dict datar skill->kategori."""
    flat = {}
    for cat, skills in taxonomy.items():
        for skill in skills:
            flat[skill.lower()] = cat
    return flat


def extract_skills(text: str, flat_skills: Dict[str, str]) -> Dict[str, List[str]]:
    """Ekstrak skill dari teks menggunakan keyword matching."""
    if not text or len(text) < 10:
        return {}
    text_lower = text.lower()
    found: Dict[str, List[str]] = {}
    for skill, category in flat_skills.items():
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.setdefault(category, [])
            if skill not in found[category]:
                found[category].append(skill)
    return found


def assess_skills(
    cv_text: str,
    target_role: str,
    job_profiles: Dict,
    flat_skills: Dict[str, str]
) -> Dict:
    """Nilai kesesuaian skill CV terhadap standar industri."""
    if target_role not in job_profiles:
        raise ValueError(f"Peran tidak tersedia: {target_role}")

    profile = job_profiles[target_role]
    cv_skills_dict = extract_skills(cv_text, flat_skills)
    cv_flat = set()
    for cat_skills in cv_skills_dict.values():
        cv_flat.update(s.lower() for s in cat_skills)

    categories = {
        "core_skills": (set(s.lower() for s in profile["core_skills"]), 0.40),
        "expected_skills": (set(s.lower() for s in profile["expected_skills"]), 0.30),
        "nice_to_have": (set(s.lower() for s in profile["nice_to_have"]), 0.15),
        "soft_skills": (set(s.lower() for s in profile["soft_skills"]), 0.15),
    }

    breakdown = {}
    overall = 0.0
    all_met, all_gap = set(), set()

    for name, (required, weight) in categories.items():
        met = cv_flat & required
        gap = required - cv_flat
        score = len(met) / max(len(required), 1) * 100
        overall += score * weight
        all_met.update(met)
        all_gap.update(gap)
        breakdown[name] = {
            "score": round(score, 1),
            "weight": f"{int(weight*100)}%",
            "met": sorted(list(met)),
            "gap": sorted(list(gap)),
            "total_required": len(required),
        }

    if overall >= 80:
        level, emoji = "SANGAT SIAP", "🟢"
    elif overall >= 60:
        level, emoji = "CUKUP SIAP", "🟡"
    elif overall >= 40:
        level, emoji = "PERLU PENINGKATAN", "🟠"
    else:
        level, emoji = "BELUM SIAP", "🔴"

    priority = []
    for s in sorted(breakdown["core_skills"]["gap"]):
        priority.append({"skill": s, "priority": "TINGGI"})
    for s in sorted(breakdown["expected_skills"]["gap"]):
        if s not in [p["skill"] for p in priority]:
            priority.append({"skill": s, "priority": "SEDANG"})

    return {
        "overall_readiness_score": round(overall, 1),
        "readiness_level": level,
        "readiness_emoji": emoji,
        "breakdown": breakdown,
        "met": sorted(list(all_met)),
        "gap": sorted(list(all_gap)),
        "priority_learning": priority[:10],
    }
