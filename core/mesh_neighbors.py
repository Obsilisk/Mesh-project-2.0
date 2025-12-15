from collections import defaultdict


def build_element_neighbors(mesh):
    node_to_elements = defaultdict(set)

    for elem_id, element in mesh.elements.items():
        for nid in element.node_ids:
            node_to_elements[nid].add(elem_id)

    neighbors = defaultdict(set)

    for elem_set in node_to_elements.values():
        for e1 in elem_set:
            for e2 in elem_set:
                if e1 != e2:
                    neighbors[e1].add(e2)

    return neighbors
