import os
import pickle

from core.mesh_loader import load_mesh
from core.mesh_neighbors import build_element_neighbors
from quality.intrinsic_metrics import compute_intrinsic_metrics
from quality.intrinsic_rules import detect_intrinsic_errors
from cad_analysis.cad_mesh_distance import compute_mesh_to_cad_distances
from cad_analysis.cad_rules import get_cad_errors
from analysis.recommendations import generate_recommendations_csv


VEHICLE = "raw/test"
OUT_DIR = "outputs"
OUT_FILE = os.path.join(OUT_DIR, "vehicle_recommendations.csv")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    cad = load_mesh(
        os.path.join(VEHICLE, "cad_NODE.csv"),
        os.path.join(VEHICLE, "cad_ELEMENT.csv")
    )

    mesh = load_mesh(
        os.path.join(VEHICLE, "first_mesh_1_NODE.csv"),
        os.path.join(VEHICLE, "first_mesh_1_ELEMENT.csv")
    )

    neighbors = build_element_neighbors(mesh)
    mesh.element_neighbors = neighbors

    intrinsic_metrics = compute_intrinsic_metrics(mesh)
    intrinsic_errors = detect_intrinsic_errors(
        mesh,
        intrinsic_metrics,
        neighbors
    )

    cad_dist = compute_mesh_to_cad_distances(mesh, cad)
    cad_errors = get_cad_errors(mesh, cad_dist)

    with open("models/vehicle_anomaly_scores.pkl", "rb") as f:
        anomaly_scores = pickle.load(f)

    generate_recommendations_csv(
        mesh=mesh,
        anomaly_scores=anomaly_scores,
        intrinsic_errors=intrinsic_errors,
        cad_errors=cad_errors,
        out_csv=OUT_FILE
    )

    print(f"✅ CSV recommendations generated → {OUT_FILE}")


if __name__ == "__main__":
    main()
