from core.mesh_loader import load_mesh
from core.mesh_neighbors import build_element_neighbors
from quality.metrics import compute_quality_metrics
from quality.rules import detect_mesh_errors

from ai.feature_builder import build_feature_matrix
from ai.risk_model import compute_risk_scores
from ai.rf_model import train_rf_model, predict_failure_probability
from ai.hybrid_risk import compute_hybrid_risk, hybrid_category

from visualization.hybrid_comparison_3d import plot_side_by_side
from visualization.mesh_error_debug_3d import plot_mesh_errors_3d


def analyze_mesh(node_csv, elem_csv):
    """
    Runs full mesh analysis pipeline.
    Returns:
        mesh object
        errors (rule-based)
        hybrid_risks (final AI risk)
    """

    mesh = load_mesh(node_csv, elem_csv)

    neighbors = build_element_neighbors(mesh)

    metrics = compute_quality_metrics(mesh)

    errors = detect_mesh_errors(metrics, neighbors)

    features = build_feature_matrix(metrics, neighbors, errors)

    rule_risks = compute_risk_scores(features)

    rf_model = train_rf_model(features, errors)

    ml_probs = predict_failure_probability(rf_model, features)

    hybrid_risks = compute_hybrid_risk(rule_risks, ml_probs)

    return mesh, errors, hybrid_risks


def main():

    print("\n=== RUNNING FIRST MESH ANALYSIS ===")

    first_mesh, first_errors, first_risks = analyze_mesh(
        "data/first_mesh/first_mesh_2_NODE.csv",
        "data/first_mesh/first_mesh_2_ELEMENT.csv"
    )

    print("\n=== RUNNING FINAL MESH ANALYSIS ===")

    final_mesh, final_errors, final_risks = analyze_mesh(
        "data/final_mesh/final_mesh_NODE.csv",
        "data/final_mesh/final_mesh_ELEMENT.csv"
    )

    plot_side_by_side(
        first_mesh,
        first_risks,
        final_mesh,
        final_risks,
        output_html="first_vs_final_mesh_comparison.html"
    )

    plot_mesh_errors_3d(
        first_mesh,
        first_errors,
        output_html="first_mesh_error_debug.html"
    )

    print("\nFINAL HYBRID HIGH-RISK ELEMENTS (FIRST MESH):")
    for eid, score in first_risks.items():
        if hybrid_category(score) == "HIGH":
            print(f"Element {eid} -> Hybrid Risk Score: {score:.2f}")

    print("\n✅ ALL VISUALIZATIONS GENERATED SUCCESSFULLY")


if __name__ == "__main__":
    main()
