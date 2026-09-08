def conjecture_1_52(G, min_size, max_size):
    import networkx as nx
    from conjectures_refutation.helpers import invariants as inv

    n = G.number_of_nodes()
    if n < min_size or n > max_size:
        return None

    A = inv.maximum_degree(G)
    alpha = inv.independence_number(G)
    B = -257.0 / 63.0 + (535.0 / 63.0) * alpha - (94.0 / 63.0) * (alpha ** 2) + (5.0 / 63.0) * (alpha ** 3)

    if not inv.is_planar(G):
        return float(abs(B - A) + 1.0)

    return float(B - A)