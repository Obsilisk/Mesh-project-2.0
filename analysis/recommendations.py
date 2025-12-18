import csv
import numpy as np

from analysis.anomaly_explainer import classify_risk
from analysis.action_mapper import map_actions


def generate_recommendations_csv(
    mesh,
    anomaly_scores,
    intrinsic_metrics,
    cad_distances,
    output_path,
    intrinsic_errors_map=None,
    cad_errors_map=None
):
    """
    Generates CSV recommendations for a single initial mesh
    using AI anomaly scores + rule explanations.
    """

    scores = np.array(list(anomaly_scores.values()))

    # Percentile-based risk
    percentiles = {
        eid: np.percentile(scores, 100 * (scores < score).mean())
        for eid, score in anomaly_scores.items()
    }

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "node_id",
            "element_id",
            "anomaly_score",
            "risk_level",
            "action_required",
            "no_of_similar_nodes",
            "primary_reason",
            "secondary_reason",
            "suggested_fix",
            "confidence"
        ])

        for eid, score in anomaly_scores.items():
            intrinsic = intrinsic_metrics[eid]
            cad_val = cad_distances.get(eid, 0.0)

            intrinsic_errors = (
                intrinsic_errors_map.get(eid, [])
                if intrinsic_errors_map else []
            )

            cad_errors = (
                cad_errors_map.get(eid, [])
                if cad_errors_map else []
            )

            risk = classify_risk(score, percentiles[eid])

            action_info = map_actions(
                intrinsic_errors=intrinsic_errors,
                cad_errors=cad_errors,
                anomaly_score=score,
                risk_level=risk
            )

            primary_action = action_info["primary_action"]
            reasons = action_info["reasons"]
            confidence = action_info["confidence"]

            # Heuristic for "similar nodes"
            similar_nodes = len(mesh.element_neighbors.get(eid, []))

            for nid in mesh.elements[eid].node_ids:
                writer.writerow([
                    nid,
                    eid,
                    round(score, 4),
                    risk,
                    primary_action,
                    similar_nodes,
                    reasons[0] if reasons else "",
                    reasons[1] if len(reasons) > 1 else "",
                    primary_action,
                    confidence
                ])
