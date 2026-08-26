import math

import networkx as nx
import numpy as np

from .invariants import invariants_functions, binary_properties_functions


def conj_a(G, min_size, max_size):
    order = G.number_of_nodes()
    if order < min_size or order > max_size:
        return None
    if not binary_properties_functions["connected"](G):
        return None
    lambda_max = invariants_functions["largest_eigenvalue"](G)
    matching_number = invariants_functions["matching_number"](G)
    return - (math.sqrt(order - 1) + 1 - lambda_max - matching_number)


def conj_b(G, min_size, max_size):
    order = G.number_of_nodes()
    if order < min_size or order > max_size:
        return None
    if not binary_properties_functions["tree"](G):
        return None
    diameter = invariants_functions["diameter"](G)
    k = math.floor(2 * diameter / 3)
    proximity = invariants_functions["proximity"](G)
    kth_largest_distance_eigenvalue = invariants_functions["kth_largest_distance_eigenvalue"](G, k)
    return -(-proximity - kth_largest_distance_eigenvalue)


def conj_c(G, min_size, max_size):
    order = G.number_of_nodes()
    if order < min_size or order > max_size:
        return None
    if not binary_properties_functions["tree"](G):
        return None
    pA, pD = invariants_functions["pA"](G), invariants_functions["pD"](G)
    m = invariants_functions["m"](G)
    return -(abs(pA / m  - (1 - pD / order)) - 0.28)


def conj_d(G, min_size, max_size):
    order = G.number_of_nodes()
    if order < min_size or order > max_size:
        return None
    if not binary_properties_functions["connected"](G):
        return None
    A = nx.adjacency_matrix(G).todense()
    eigenvalues = np.linalg.eigvals(A)
    second_largest_eigenvalues = np.sort(eigenvalues)[-2]
    harmonic_index = invariants_functions["harmonic_index"](G)
    return -(second_largest_eigenvalues - harmonic_index)


def conj_e(G, min_size, max_size):
    order = G.number_of_nodes()
    if order < min_size or order > max_size:
        return None
    if not binary_properties_functions["tree"](G):
        return None
    return (order + 1) / 4 - invariants_functions["modified_zagreb_2"](G)


def conj_f(G, min_size, max_size):
    order = G.number_of_nodes()
    if order < min_size or order > max_size:
        return None
    if not binary_properties_functions["tree"](G):
        return None
    gamma = invariants_functions["domination_number"](G)
    zagreb = invariants_functions["modified_zagreb_2"](G)
    return -((1 - gamma) / (2 * order - 2 * gamma) + (gamma + 1) / 2 - zagreb)


def conj_g(G, min_size, max_size):
    order = G.number_of_nodes()
    if order < min_size or order > max_size:
        return None
    if not binary_properties_functions["connected"](G):
        return None
    lambda_max = invariants_functions["largest_eigenvalue"](G)
    proximity_ = invariants_functions["proximity"](G)
    return -(lambda_max * proximity_ - order + 1)


def conj_h(G, min_size, max_size):
    order = G.number_of_nodes()
    if order < min_size or order > max_size:
        return None
    if not binary_properties_functions["connected"](G):
        return None
    proximity = invariants_functions["proximity"](G)
    connectivity = invariants_functions["connectivity"](G)
    term = connectivity * proximity
    if order % 2 == 0:
        return -(0.5 * (order ** 2 / (order - 1)) * (1 - math.cos(math.pi / order)) - term)
    else:
        return -(0.5 * (order + 1) * (1 - math.cos(math.pi / order)) - term)


def conj_i(G, min_size, max_size):
    order = G.number_of_nodes()
    if order < min_size or order > max_size:
        return None
    if not binary_properties_functions["connected"](G):
        return None
    lambda_max = invariants_functions["largest_eigenvalue"](G)
    alpha = invariants_functions["independence_number"](G)
    return -(math.sqrt(order - 1) - order + 1 - lambda_max + alpha)


def conj_j(G, min_size, max_size):
    order = G.number_of_nodes()
    if order < min_size or order > max_size:
        return None
    if not binary_properties_functions["connected"](G):
        return None
    randic_index = invariants_functions["randic_index"](G)
    alpha = invariants_functions["independence_number"](G)
    return -(randic_index + alpha - order + 1 - math.sqrt(order - 1))