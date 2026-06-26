def classify_attack(prompt: str):

    p = prompt.lower()

    if "system prompt" in p:
        return "System Prompt Extraction"

    if "act as" in p and ("unrestricted" in p or "no rules" in p):
        return "Jailbreak Attempt"

    if "ignore" in p or "bypass" in p or "override" in p:
        return "Policy Evasion"

    if "secret" in p or "confidential" in p:
        return "Data Exfiltration"

    return "Safe Request"