def conjecture_1_54(G, min_size, max_size):
    import networkx as nx
    from conjectures_refutation.helpers import invariants as inv

    n = G.number_of_nodes()
    if n < min_size or n > max_size:
        return None

    avg = inv.average_degree(G)
    tau = inv.vertex_cover_number(G)

    A = avg
    B = 1.0 + (5.0 / 3.0) * tau - (21.0 / 92.0) * (tau ** 2) + (1.0 / 97.0) * (tau ** 3)

    if not inv.is_planar(G):
        return float(abs(B - A) + 1.0)

    return float(B - A)