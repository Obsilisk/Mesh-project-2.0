def map_actions(
    intrinsic_errors,
    cad_errors,
    anomaly_score,
    risk_level
):
    """
    Clean, prescriptive AI-aware action mapper.
    Produces ONE clear engineering action.
    """

    all_errors = set(intrinsic_errors) | set(cad_errors)

    # -----------------------------
    # CONNECTIVITY ISSUES (HIGHEST PRIORITY)
    # -----------------------------
    if "MISSING_NEIGHBOR" in all_errors or "ORPHAN_NODE" in all_errors:
        return {
            "primary_action": "REMESH_REGION",
            "action_scope": "REGION",
            "reason": "Mesh connectivity broken",
            "confidence": 0.95
        }

    # -----------------------------
    # HIGH RISK (AI DRIVEN)
    # -----------------------------
    if risk_level == "HIGH":
        if (
            "BAD_ASPECT_RATIO" in all_errors
            or "HIGH_SKEWNESS" in all_errors
            or anomaly_score > 0.15
        ):
            return {
                "primary_action": "MOVE_NODES",
                "action_scope": "NODE",
                "reason": "Severely distorted element geometry",
                "confidence": min(0.95, 0.6 + anomaly_score)
            }

        if "CAD_DEVIATION_HIGH" in all_errors:
            return {
                "primary_action": "PROJECT_TO_CAD",
                "action_scope": "NODE",
                "reason": "Large deviation from CAD surface",
                "confidence": min(0.9, 0.55 + anomaly_score)
            }

        return {
            "primary_action": "LOCAL_REMESH",
            "action_scope": "ELEMENT",
            "reason": "Statistically abnormal mesh region",
            "confidence": min(0.9, 0.55 + anomaly_score)
        }

    # -----------------------------
    # MEDIUM RISK
    # -----------------------------
    if risk_level == "MEDIUM":
        if "BAD_TRANSITION" in all_errors or "SMALL_AREA" in all_errors:
            return {
                "primary_action": "SMOOTH_MESH",
                "action_scope": "NODE",
                "reason": "Poor mesh transition detected",
                "confidence": min(0.8, 0.5 + anomaly_score)
            }

        if "CAD_DEVIATION_HIGH" in all_errors:
            return {
                "primary_action": "PROJECT_TO_CAD",
                "action_scope": "NODE",
                "reason": "Moderate CAD mismatch",
                "confidence": min(0.8, 0.5 + anomaly_score)
            }

        return {
            "primary_action": "CHECK_GEOMETRY",
            "action_scope": "ELEMENT",
            "reason": "Moderate anomaly without explicit rule violation",
            "confidence": min(0.75, 0.45 + anomaly_score)
        }

    # -----------------------------
    # LOW RISK — NO CSV ENTRY
    # -----------------------------
    return {
        "primary_action": "NO_ACTION",
        "action_scope": "NONE",
        "reason": "Mesh within learned distribution",
        "confidence": round(0.4 + anomaly_score, 2)
    }
