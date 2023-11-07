import networkx as nx
from typing import List, Tuple, Dict
from ast import literal_eval

####################################################

@nx.utils.decorators.nodes_or_number([0, 1])
def custom_grid_2d_graph(m, n, node_color: str = 'tab:red') -> nx.Graph:
    """Returns the two-dimensional grid graph.

    The grid graph has each node connected to its four nearest neighbors.
    """
    G = nx.empty_graph(0)
    row_name, rows = m
    col_name, cols = m
    G.add_nodes_from((2*i, 2*j) for i in rows for j in cols)
    G.add_edges_from(((2*i, 2*j), (2*pi, 2*j )) for pi, i in nx.utils.pairwise(rows) for j in cols)
    G.add_edges_from(((2*i, 2*j), (2*i , 2*pj)) for i in rows for pj, j in nx.utils.pairwise(cols))
    # Both directions for directed
    if G.is_directed():
        G.add_edges_from((v, u) for u, v in G.edges())
    return G

####################################################

def is_stabilizer(stab: str, pauli: List = ['x', 'X']) -> bool:
    """Check if stabilizers is in the format X(0,2).X(2,2).X(0,0)"""
    s = stab.split('.')
    is_x_type = s[0][0] in pauli
    for term in s[1:]:
        is_x_type = is_x_type and term[0] in pauli
    return is_x_type

####################################################

def shift_stabilizer(stab: str, shift: str) -> str:
    new_stab = ''
    s = literal_eval(shift)
    for idx, term in enumerate(stab.split('.')):
        old = literal_eval(term[1:])
        if idx > 0:
            new_stab += '.'
        new_stab += term[0] + '(' + str(old[0]+s[0]) + ',' + str(old[1]+s[1]) + ')'
    return new_stab

####################################################

def add_stabilizer_to_graph(G: nx.Graph, stab: str) -> Tuple[nx.Graph, Tuple[int, int]]:
    """Parse stabilizers in the format X(0,2).X(2,2).X(0,0)"""
    # Parse nodes involved in stabilizer.
    nodes = []
    avg_x, avg_y = 0, 0
    for term in stab.split('.'):
        node = literal_eval(term[1:])
        avg_x += node[0]
        avg_y += node[1]
        nodes.append(node)
    assert len(nodes) ==2  or len(nodes) == 4
    avg_x = int(avg_x/len(nodes))
    avg_y = int(avg_y/len(nodes))
    # Coordinates of ancilla node.
    is_vert_line = len(nodes)==2 and nodes[0][0] == nodes[1][0]
    is_horz_line = len(nodes)==2 and nodes[0][1] == nodes[1][1]
    if is_vert_line:
        if avg_x == 0:
            ax = -1
        else:
            ax = avg_x + 1
        ay = avg_y
    elif is_horz_line:
        ax = avg_x
        if avg_y == 0:
            ay = -1
        else:
            ay = avg_y + 1
    else:
        ax = avg_x
        ay = avg_y
    ancilla = (ax, ay)
    # Add ancilla node and edges.
    G.add_node(ancilla)
    G.add_edges_from([(n, ancilla) for n in nodes])
    return G, ancilla

####################################################

def get_options_for_draw(G: nx.Graph, x_ancillas: List, z_ancillas: List) -> Dict:
    node_color = []
    for n in G.nodes:
        if n in x_ancillas:
            node_color.append('tab:blue')
        elif n in z_ancillas:
            node_color.append('tab:red')
        else:
            node_color.append('yellow')
    options = {
        'with_labels': True,
        'node_color': node_color,
        'node_size': 400,
        'width': 1,
        'font_size': 10
    }
    return options

####################################################

def remove_edges_between_data(G: nx.Graph) -> nx.Graph:
    for e in G.edges:
        do_remove = True
        # If both nodes have only even coordinate, remove the edge.
        do_remove = do_remove and (e[0][0]%2==0 and e[0][1]%2==0)
        do_remove = do_remove and (e[1][0]%2==0 and e[1][1]%2==0)
        if do_remove:
            G.remove_edge(e[0], e[1])
    return G

####################################################
