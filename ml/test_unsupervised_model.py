import os
import pickle
import numpy as np

from core.mesh_loader import load_mesh
from core.mesh_neighbors import build_element_neighbors
from quality.intrinsic_metrics import compute_intrinsic_metrics
from cad_analysis.cad_mesh_distance import compute_mesh_to_cad_distances
from ai.feature_builder import build_feature_vector

# --------------------------------------------------
# PATHS
# --------------------------------------------------
VEHICLE_TEST = "raw/08_"

MODEL_PATH = "models/unsupervised_iforest.pkl"
SCALER_PATH = "models/feature_scaler.pkl"

# --------------------------------------------------
# LOAD MODEL & SCALER
# --------------------------------------------------
with open("models/unsupervised_iforest.pkl", "rb") as f:
    model = pickle.load(f)

with open("models/feature_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)



def main():
    print("🚗 Testing on vehicle 08_")

    cad = load_mesh(
        os.path.join(VEHICLE_TEST, "cad_NODE.csv"),
        os.path.join(VEHICLE_TEST, "cad_ELEMENT.csv")
    )

    # Pick ONE first mesh (you can loop later)
    mesh = load_mesh(
        os.path.join(VEHICLE_TEST, "first_mesh_2_NODE.csv"),
        os.path.join(VEHICLE_TEST, "first_mesh_2_ELEMENT.csv")
    )

    # Build neighbors
    mesh.element_neighbors = build_element_neighbors(mesh)

    # Compute features
    intrinsic = compute_intrinsic_metrics(mesh)
    cad_dists = compute_mesh_to_cad_distances(mesh, cad)

    element_ids = []
    X = []

    for eid in mesh.elements:
        vec = build_feature_vector(
            eid=eid,
            mesh=mesh,
            intrinsic_metrics=intrinsic,
            cad_distances=cad_dists
        )
        X.append(vec)
        element_ids.append(eid)

    X = np.array(X)
    X_scaled = scaler.transform(X)
    scores = model.decision_function(X_scaled)

    # Isolation Forest anomaly score
    # Higher = more anomalous
    anomaly_scores = -model.decision_function(X_scaled)

    print("\n🔎 Sample anomaly scores:")
    for i in range(10):
        print(f"Element {element_ids[i]} → Anomaly score: {anomaly_scores[i]:.4f}")

    # Store results
    results = dict(zip(element_ids, anomaly_scores))

    print(f"\n✅ Computed anomaly scores for {len(results)} elements")

    # Save for next stages
    os.makedirs("models", exist_ok=True)
    with open("models/vehicle_08_anomaly_scores.pkl", "wb") as f:
        pickle.dump(results, f)

    print("📦 Saved anomaly scores → models/vehicle_08_anomaly_scores.pkl")


if __name__ == "__main__":
    main()
