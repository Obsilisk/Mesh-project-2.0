import csv
from .mesh_objects import Mesh, Node, Element


def load_mesh(node_csv_path, element_csv_path):
    mesh = Mesh()

    with open(node_csv_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        for row in reader:
            node_id, x, y, z = row
            mesh.nodes[int(node_id)] = Node(node_id, x, y, z)

    with open(element_csv_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        for row in reader:
            elem_id, elem_type, *node_ids = row
            node_ids = [int(float(nid)) for nid in node_ids if nid.strip()]
            mesh.elements[int(elem_id)] = Element(elem_id, node_ids)

    return mesh