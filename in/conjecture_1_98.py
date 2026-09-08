def conjecture_1_98(G, min_size, max_size):
    import networkx as nx
    from conjectures_refutation.helpers import invariants as inv

    n = G.number_of_nodes()
    if n < min_size or n > max_size:
        return None

    if not inv.is_connected(G):
        return float(nx.number_connected_components(G))

    diam = inv.diameter(G)
    gamma = inv.domination_number(G)

    A = diam
    B = 3.0 - (10.0 / 3.0) * gamma + (1.5) * (gamma ** 2) - (1.0 / 6.0) * (gamma ** 3)

    if not inv.is_claw_free(G):
        return float(abs(A - B) + 1.0)

    return float(A - B)

# pi / delta / alpha / m / gamma