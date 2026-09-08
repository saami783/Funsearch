def conjecture_96(G, min_size, max_size):
    import networkx as nx
    from conjectures_refutation.helpers import invariants as inv

    n = G.number_of_nodes()
    if n < min_size or n > max_size:
        return None

    Delta = inv.maximum_degree(G)
    t = inv.triangle_number(G)

    A = Delta
    B = (151.0 / 35.0) + (14.0 / 61.0) * t

    if not inv.is_claw_free(G):
        return float(abs(B - A) + 1.0)
    
    return float(B - A)


