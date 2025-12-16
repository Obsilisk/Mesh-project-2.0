from core.mesh_loader import load_mesh
from core.mesh_neighbors import build_element_neighbors
from quality.intrinsic_metrics import compute_intrinsic_metrics
from quality.intrinsic_rules import detect_intrinsic_errors
from cad_analysis.cad_mesh_distance import compute_mesh_to_cad_distances
from cad_analysis.cad_rules import detect_cad_related_errors
from analysis.recommendations import aggregate_mesh_analysis

# Load meshes
mesh = load_mesh(
    "data/first_mesh/first_mesh_1_NODE.csv",
    "data/first_mesh/first_mesh_1_ELEMENT.csv"
)

cad = load_mesh(
    "data/cad/cad_NODE.csv",
    "data/cad/cad_ELEMENT.csv"
)

# Intrinsic analysis
neighbors = build_element_neighbors(mesh)
metrics = compute_intrinsic_metrics(mesh)
intrinsic_errors = detect_intrinsic_errors(mesh, metrics, neighbors)

# CAD analysis
distances = compute_mesh_to_cad_distances(mesh, cad)
cad_errors = detect_cad_related_errors(mesh, distances)

# Final aggregation
final_report = aggregate_mesh_analysis(intrinsic_errors, cad_errors)

# Print high severity elements
print("\nHIGH SEVERITY ELEMENTS:")
for eid, info in final_report.items():
    if info["severity"] == "HIGH":
        print(f"\nElement {eid}")
        print("Intrinsic Errors:", info["intrinsic_errors"])
        print("CAD Errors:", info["cad_errors"])
        print("Recommendations:")
        for r in info["recommendations"]:
            print(" -", r)
