def map_actions(
    intrinsic_errors,
    cad_errors,
    anomaly_score,
    risk_level
):
   
    all_errors = set(intrinsic_errors) | set(cad_errors)

    # -----------------------------
    # CONNECTIVITY ISSUES
    # -----------------------------
    if "MISSING_NEIGHBOR" in all_errors or "ORPHAN_NODE" in all_errors:
        return {
            "primary_action": "Fix connectivity",
            "confidence": 0.95
        }

    # -----------------------------
    # CAD DEVIATION
    # -----------------------------
    if "CAD_DEVIATION_HIGH" in all_errors:
        return {
            "primary_action": "Project to CAD",
            "confidence": min(0.9, 0.6 + anomaly_score)
        }

    # -----------------------------
    # SEVERE SHAPE DISTORTION
    # -----------------------------
    if (
        "BAD_ASPECT_RATIO" in all_errors
        or "HIGH_SKEWNESS" in all_errors
    ):
        return {
            "primary_action": "Reduce skew",
            "confidence": min(0.9, 0.6 + anomaly_score)
        }

    # -----------------------------
    # SMALL / DEGRADED ELEMENTS
    # -----------------------------
    if "SMALL_AREA" in all_errors:
        return {
            "primary_action": "Delete node",
            "confidence": min(0.85, 0.55 + anomaly_score)
        }

    # -----------------------------
    # POOR TRANSITION / DENSITY
    # -----------------------------
    if "BAD_TRANSITION" in all_errors:
        return {
            "primary_action": "Add node",
            "confidence": min(0.85, 0.55 + anomaly_score)
        }

    # -----------------------------
    # AI-ONLY ANOMALY (NO RULE HIT)
    # -----------------------------
    if risk_level in ["HIGH", "MEDIUM"]:
        return {
            "primary_action": "Remesh area",
            "confidence": min(0.8, 0.5 + anomaly_score)
        }

    # -----------------------------
    # ACCEPTABLE MESH
    # -----------------------------
    return {
        "primary_action": "Accept mesh",
        "confidence": round(0.4 + anomaly_score, 2)
    }
