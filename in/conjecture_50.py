def conjecture_50(G, min_size, max_size):
    import networkx as nx
    from conjectures_refutation.helpers import invariants as inv

    n = G.number_of_nodes()
    if n < min_size or n > max_size:
        return None

    m = inv.size(G)
    alpha = inv.independence_number(G)

    A = m
    B = -(243.0 / 14.0) + (2032.0 / 73.0) * alpha - (146.0 / 31.0) * (alpha ** 2) + (3.0 / 13.0) * (alpha ** 3)

    if not inv.is_planar(G):
        return float(abs(B - A) + 1.0)

    return float(B - A)