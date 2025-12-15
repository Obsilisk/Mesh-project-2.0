from ai.risk_model import risk_category


def generate_scorecard(mesh, metrics, errors, risks):
    total_elements = len(metrics)
    total_nodes = len(mesh.nodes)

    avg_aspect = sum(m["aspect_ratio"] for m in metrics.values()) / total_elements
    max_aspect = max(m["aspect_ratio"] for m in metrics.values())

    small_area_count = sum(1 for m in metrics.values() if m["area"] < 1.0)

    error_summary = {}
    for errs in errors.values():
        for e in errs:
            error_summary[e] = error_summary.get(e, 0) + 1

    risk_summary = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for score in risks.values():
        risk_summary[risk_category(score)] += 1

    if risk_summary["HIGH"] > 0:
        overall_risk = "HIGH"
    elif risk_summary["MEDIUM"] > 0:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    return {
        "total_nodes": total_nodes,
        "total_elements": total_elements,
        "avg_aspect_ratio": round(avg_aspect, 3),
        "max_aspect_ratio": round(max_aspect, 3),
        "small_area_elements": small_area_count,
        "error_summary": error_summary,
        "risk_summary": risk_summary,
        "overall_mesh_risk": overall_risk
    }
 