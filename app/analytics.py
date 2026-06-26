from datetime import datetime

# -----------------------------
# GLOBAL STATS STORE
# -----------------------------
stats = {
    "total": 0,
    "blocked": 0,
    "safe": 0,
    "suspicious": 0,

    "attack_types": {},

    "risk_levels": {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0
    },

    # timeline (SOC-style event history)
    "timeline": [],

    # live feed (UI)
    "recent_events": []
}


# -----------------------------
# UPDATE STATS (SOC ENGINE)
# -----------------------------
def update_stats(result: dict):

    stats["total"] += 1

    category = result.get("category", "safe")
    attack_type = result.get("attack_type", "unknown")
    risk = result.get("risk_level", "LOW")

    # ---------------- CATEGORY COUNT ----------------
    if category == "blocked":
        stats["blocked"] += 1

    elif category == "suspicious":
        stats["suspicious"] += 1

    else:
        stats["safe"] += 1
        attack_type = "Safe"

    # ---------------- ATTACK TYPE TRACKING ----------------
    stats["attack_types"][attack_type] = stats["attack_types"].get(attack_type, 0) + 1

    # ---------------- RISK LEVEL SAFE INCREMENT ----------------
    if risk not in stats["risk_levels"]:
        risk = "LOW"

    stats["risk_levels"][risk] += 1

    # ---------------- EVENT OBJECT (SOC FORMAT) ----------------
    event = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "attack_type": attack_type,
        "risk": risk,
        "category": category
    }

    # ---------------- TIMELINE (LONG TERM HISTORY) ----------------
    stats["timeline"].append(event)
    stats["timeline"] = stats["timeline"][-30:]

    # ---------------- LIVE FEED (DASHBOARD) ----------------
    stats["recent_events"].append(event)
    stats["recent_events"] = stats["recent_events"][-10:]


# -----------------------------
# GET STATS (API OUTPUT)
# -----------------------------
def get_stats():
    return stats
