import pandas as pd

from core.mesh_loader import load_mesh
from analysis.mesh_validation import (
    validate_mesh_changes,
    element_changed
)

VEHICLE = "raw/test"


def main():
    # Load meshes
    mesh_init = load_mesh(
        f"{VEHICLE}/first_mesh_1_NODE.csv",
        f"{VEHICLE}/first_mesh_1_ELEMENT.csv"
    )

    mesh_final = load_mesh(
        f"{VEHICLE}/final_mesh_NODE.csv",
        f"{VEHICLE}/final_mesh_ELEMENT.csv"
    )

    cad_init = load_mesh(
        f"{VEHICLE}/cad_NODE.csv",
        f"{VEHICLE}/cad_ELEMENT.csv"
    )

    cad_final = cad_init  # same CAD

    # Load full recommendations CSV (do NOT modify)
    df = pd.read_csv("outputs/vehicle_recommendations.csv")
    all_recs = df.to_dict(orient="records")

    # Actionable (MEDIUM + HIGH)
    actionable_recs = [
        r for r in all_recs
        if r["ai_severity"] in ["MEDIUM", "HIGH"]
    ]

    # LOW-risk (for stability check)
    low_risk_recs = [
        r for r in all_recs
        if r["ai_severity"] == "LOW"
    ]

    # -----------------------------
    # Actionable validation
    # -----------------------------
    metrics = validate_mesh_changes(
        mesh_init,
        mesh_final,
        actionable_recs,
        cad_init,
        cad_final
    )

    print("\n🔎 VALIDATION RESULTS (MEDIUM + HIGH)")
    for k, v in metrics.items():
        print(f"{k}: {v:.3f}")

    # -----------------------------
    # LOW-risk stability validation
    # -----------------------------
    stable = 0
    for rec in low_risk_recs:
        eid = rec["element_id"]
        if not element_changed(eid, mesh_init, mesh_final):
            stable += 1

    stability_rate = (
        stable / len(low_risk_recs)
        if low_risk_recs else 0.0
    )

    print("\n🟢 LOW RISK STABILITY")
    print(f"stability_rate: {stability_rate:.3f}")


if __name__ == "__main__":
    main()
