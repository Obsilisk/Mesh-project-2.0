def map_actions(
    intrinsic_errors,
    cad_errors,
    anomaly_score,
    risk_level
):
    """
    AI-aware action mapper.
    Combines rule-based explanations with ML severity.
    """

    actions = []
    reasons = []

    all_errors = set(intrinsic_errors) | set(cad_errors)

    # -----------------------------
    # HIGH RISK — AI decides first
    # -----------------------------
    if risk_level == "HIGH":
        if (
            "BAD_ASPECT_RATIO" in all_errors
            or "HIGH_SKEWNESS" in all_errors
            or anomaly_score > 0.15
        ):
            actions.append("DELETE & REMESH")
            reasons.append("Severely distorted element")

        elif "CAD_DEVIATION_HIGH" in all_errors:
            actions.append("MOVE NODES TO CAD")
            reasons.append("Large CAD deviation")

    # -----------------------------
    # MEDIUM RISK
    # -----------------------------
    elif risk_level == "MEDIUM":
        if "BAD_TRANSITION" in all_errors or "SMALL_AREA" in all_errors:
            actions.append("REFINE LOCALLY")
            reasons.append("Poor mesh transition")

        if "CAD_DEVIATION_HIGH" in all_errors:
            actions.append("MOVE NODES TO CAD")
            reasons.append("CAD mismatch")

    # -----------------------------
    # LOW RISK
    # -----------------------------
    else:
        if all_errors:
            actions.append("MONITOR")
            reasons.append("Minor deviations detected")
        else:
            actions.append("NO ACTION")
            reasons.append("Mesh within learned distribution")

    # -----------------------------
    # Connectivity overrides
    # -----------------------------
    if "MISSING_NEIGHBOR" in all_errors or "ORPHAN_NODE" in all_errors:
        actions = ["ADD CONNECTIVITY"]
        reasons = ["Mesh connectivity issue detected"]

    # -----------------------------
    # Confidence heuristic
    # -----------------------------
    confidence = min(0.95, 0.55 + anomaly_score)

    return {
        "primary_action": actions[0],
        "all_actions": actions,
        "reasons": reasons,
        "confidence": round(confidence, 2)
    }
