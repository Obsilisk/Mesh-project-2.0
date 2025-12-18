import os
import pickle
import json
import numpy as np
from tqdm import tqdm

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from core.mesh_loader import load_mesh
from core.mesh_neighbors import build_element_neighbors
from quality.intrinsic_metrics import compute_intrinsic_metrics
from cad_analysis.cad_mesh_distance import compute_mesh_to_cad_distances
from ai.feature_builder import build_feature_vector


RAW_ROOT = "raw"
TRAIN_VEHICLES = ["01_", "02_", "03_", "04_", "05_", "06_", "07_"]

MODEL_OUT = "models/unsupervised_iforest.pkl"
SCALER_OUT = "models/feature_scaler.pkl"
STATS_OUT = "models/feature_stats.json"


def collect_training_features():
    X = []

    print("🔍 Collecting training data from vehicles 01_ → 07_")

    for vehicle in TRAIN_VEHICLES:
        vehicle_path = os.path.join(RAW_ROOT, vehicle)

        cad_nodes = os.path.join(vehicle_path, "cad_NODE.csv")
        cad_elems = os.path.join(vehicle_path, "cad_ELEMENT.csv")

        if not os.path.exists(cad_nodes):
            continue

        cad_mesh = load_mesh(cad_nodes, cad_elems)

        for file in os.listdir(vehicle_path):
            if not file.startswith("first_mesh_") or not file.endswith("_NODE.csv"):
                continue

            mesh_id = file.replace("_NODE.csv", "")
            node_file = os.path.join(vehicle_path, f"{mesh_id}_NODE.csv")
            elem_file = os.path.join(vehicle_path, f"{mesh_id}_ELEMENT.csv")

            if not os.path.exists(elem_file):
                continue

            mesh = load_mesh(node_file, elem_file)
            mesh.element_neighbors = build_element_neighbors(mesh)


            intrinsic = compute_intrinsic_metrics(mesh)
            cad_dists = compute_mesh_to_cad_distances(mesh, cad_mesh)

            for eid in mesh.elements:
                feature_vec = build_feature_vector(
                    eid,
                    intrinsic_metrics=intrinsic,
                    cad_distances=cad_dists,
                    mesh=mesh
                )
                X.append(feature_vec)

    return np.array(X)


def main():
    X = collect_training_features()

    print(f"✅ Collected {X.shape[0]} elements for training")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    stats = {
        "mean": scaler.mean_.tolist(),
        "std": scaler.scale_.tolist()
    }

    model = IsolationForest(
        n_estimators=300,
        contamination="auto",
        random_state=42
    )

    model.fit(X_scaled)

    os.makedirs("models", exist_ok=True)

    with open(MODEL_OUT, "wb") as f:
        pickle.dump(model, f)

    with open(SCALER_OUT, "wb") as f:
        pickle.dump(scaler, f)

    with open(STATS_OUT, "w") as f:
        json.dump(stats, f, indent=2)

    print("🎯 Unsupervised model training complete")
    print(f"📦 Model saved → {MODEL_OUT}")
    print(f"📦 Scaler saved → {SCALER_OUT}")
    print(f"📊 Stats saved → {STATS_OUT}")


if __name__ == "__main__":
    main()
