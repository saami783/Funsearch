def conjecture_53(G, min_size, max_size):
    import networkx as nx
    from conjectures_refutation.helpers import invariants as inv

    n = G.number_of_nodes()
    if n < min_size or n > max_size:
        return None

    avg = inv.average_degree(G)
    alpha = inv.independence_number(G)

    A = avg
    B = (17.0 / 7.0) + (81.0 / 56.0) * alpha - (21.0 / 94.0) * (alpha ** 2) + (1.0 / 100.0) * (alpha ** 3)

    if not inv.is_planar(G):
        return float(abs(B - A) + 1.0)

    return float(B - A)