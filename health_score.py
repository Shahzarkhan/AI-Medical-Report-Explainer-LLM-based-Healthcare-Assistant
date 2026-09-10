import re

def calculate_health_score(report_text):
    report = report_text.lower()

    score = 100
    abnormalities = 0

    keywords = [
        "high",
        "low",
        "deficiency",
        "abnormal",
        "positive"
    ]

    # Count all abnormal keywords
    for word in keywords:
        abnormalities += len(re.findall(word, report))

    # Deduct score
    score -= abnormalities * 5
    score = max(score, 0)

    # Risk Level
    if score >= 85:
        risk = "Low"
    elif score >= 70:
        risk = "Medium"
    else:
        risk = "High"

    normal = max(0, 65 - abnormalities)

    return score, risk, abnormalities, normal