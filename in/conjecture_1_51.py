def conjecture_1_51(G, min_size, max_size):
    import networkx as nx
    from conjectures_refutation.helpers import invariants as inv

    n = G.number_of_nodes()
    if n < min_size or n > max_size:
        return None

    d = inv.density(G)
    alpha = inv.independence_number(G)

    A = d
    B = (116.0 / 97.0) - (8.0 / 49.0) * alpha + (1.0 / 100.0) * (alpha ** 2)

    if not inv.is_planar(G):
        return float(abs(B - A) + 1.0)

    return float(B - A)