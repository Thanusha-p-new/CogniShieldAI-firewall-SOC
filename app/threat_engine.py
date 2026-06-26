def compute_threat_score(regex_hit: bool, similarity: float, soft_hit: bool = False, intent_score: float = 0):
    """
    Hybrid threat scoring engine (FINAL VERSION)
    Combines:
    - Regex signals
    - Semantic similarity
    - Soft manipulation boost
    - Intent score
    """

    score = 0
    methods = []

    # -------------------
    # 1. Regex contribution (strong signal)
    # -------------------
    if regex_hit:
        score += 55
        methods.append("Regex")

    # -------------------
    # 2. Semantic contribution (scaled safely)
    # -------------------
    semantic_score = min(similarity * 100, 45)  # CAP semantic impact
    if similarity > 0:
        score += semantic_score
        methods.append("Semantic")

    # -------------------
    # 3. Soft manipulation boost (IMPORTANT UPGRADE)
    # -------------------
    if soft_hit:
        score += 20
        methods.append("SoftPattern")

    # -------------------
    # 4. Intent score contribution
    # -------------------
    score += intent_score * 0.35  # weighted impact

    # -------------------
    # 5. Normalize final score
    # -------------------
    score = min(score, 100)

    # -------------------
    # 6. Risk classification (improved thresholds)
    # -------------------
    if score >= 75:
        risk = "HIGH"
    elif score >= 40:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "threat_score": round(score, 2),
        "risk_level": risk,
        "detection_methods": methods
    }
