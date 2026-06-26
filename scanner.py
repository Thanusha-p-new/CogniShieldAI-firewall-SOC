import re
from app.classifier import classify_attack
from app.vector_db import semantic_scan
from app.threat_engine import compute_threat_score

PATTERNS = [
    r"ignore.*instructions",
    r"ignore.*previous.*instructions",
    r"disregard.*instructions",
    r"developer mode",
    r"dan mode",
    r"system prompt",
    r"reveal.*prompt",
    r"reveal.*system",
    r"override.*safety",
    r"bypass.*restrictions",
    r"bypass.*filters",
    r"forget.*instructions",
    r"act as.*unrestricted",
    r"you are now.*unrestricted",
    r"ignore.*rules",
    r"no.*rules",
    r"no.*restrictions",
]

SOFT_PATTERNS = [
    r"act as if.*no rules",
    r"pretend.*no restrictions",
    r"simulate.*unrestricted",
    r"roleplay.*no limitations",
    r"answer as if.*no policy",
    r"without following.*rules",
]


def compute_intent_score(prompt: str) -> float:
    p = prompt.lower()
    score = 0

    risky_phrases = [
        "ignore instructions",
        "ignore rules",
        "bypass restrictions",
        "override safety",
        "developer mode",
        "dan mode",
        "system prompt",
        "no rules",
        "no restrictions",
    ]

    for phrase in risky_phrases:
        if phrase in p:
            score += 40

    if "act as" in p:
        score += 15
    if "pretend" in p:
        score += 10
    if "simulate" in p:
        score += 10
    if "roleplay" in p:
        score += 10

    return min(score, 100)


def scan_prompt(prompt: str):

    detection_methods = []

    regex_hit = any(re.search(p, prompt, re.IGNORECASE) for p in PATTERNS)
    soft_hit = any(re.search(p, prompt, re.IGNORECASE) for p in SOFT_PATTERNS)

    if regex_hit:
        detection_methods.append("regex")
    if soft_hit:
        detection_methods.append("soft_pattern")

    # semantic detection
    try:
        result = semantic_scan(prompt)
        similarity = float(result.get("similarity", 0.0))
    except:
        similarity = 0.0

    if similarity > 0.15:
        detection_methods.append("semantic")

    # base threat score
    base_score = float(compute_threat_score(regex_hit, similarity).get("threat_score", 0))

    intent_score = compute_intent_score(prompt)
    semantic_score = similarity * 100

    # balanced scoring (FIXED)
    final_score = max(
        base_score,
        semantic_score * 0.8,
        intent_score * 0.6
    )

    # boosts
    if soft_hit:
        final_score += 10
    if regex_hit:
        final_score += 20

    final_score = min(final_score, 100)

    # classification (FIXED THRESHOLDS)
    if regex_hit and final_score >= 65:
        category = "blocked"
        risk_level = "CRITICAL"
        blocked = True

    elif final_score >= 60:
        category = "blocked"
        risk_level = "HIGH"
        blocked = True

    elif final_score >= 35:
        category = "suspicious"
        risk_level = "MEDIUM"
        blocked = False

    else:
        category = "safe"
        risk_level = "LOW"
        blocked = False

    try:
        attack_type = classify_attack(prompt)
    except:
        attack_type = "Unclassified"

    return {
        "blocked": blocked,
        "category": category,
        "attack_type": attack_type,
        "risk_level": risk_level,
        "threat_score": round(final_score, 2),
        "confidence": round(similarity, 3),
        "intent_score": round(intent_score, 2),
        "detection_methods": detection_methods,
        "reason": category
    }