def conjecture_1_55(G, min_size, max_size):
    import networkx as nx
    from conjectures_refutation.helpers import invariants as inv

    n = G.number_of_nodes()
    if n < min_size or n > max_size:
        return None

    t = inv.triangle_number(G)
    tau = inv.vertex_cover_number(G)

    A = t
    B = -(125.0 / 8.0) + (865.0 / 48.0) * tau - (5.0 / 2.0) * (tau ** 2) + (5.0 / 48.0) * (tau ** 3)

    if not inv.is_planar(G):
        return float(abs(B - A) + 1.0)

    return float(B - A)