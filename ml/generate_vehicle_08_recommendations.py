import os
import pickle

from core.mesh_loader import load_mesh
from core.mesh_neighbors import build_element_neighbors
from quality.intrinsic_metrics import compute_intrinsic_metrics
from cad_analysis.cad_mesh_distance import compute_mesh_to_cad_distances
from analysis.recommendations import generate_recommendations_csv


VEHICLE = "raw/08_"
OUT_DIR = "outputs"
OUT_FILE = os.path.join(OUT_DIR, "vehicle_08_recommendations.csv")


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

    mesh.element_neighbors = build_element_neighbors(mesh)

    intrinsic = compute_intrinsic_metrics(mesh)
    cad_dist = compute_mesh_to_cad_distances(mesh, cad)

    with open("models/vehicle_08_anomaly_scores.pkl", "rb") as f:
        anomaly_scores = pickle.load(f)

    generate_recommendations_csv(
        mesh,
        anomaly_scores,
        intrinsic,
        cad_dist,
        OUT_FILE
    )

    print(f"✅ CSV recommendations generated → {OUT_FILE}")


if __name__ == "__main__":
    main()
