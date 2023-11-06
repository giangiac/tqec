import networkx as nx
from typing import List, Tuple
from ast import literal_eval
import ipywidgets as widgets
import matplotlib.pyplot as plt # Import graphical library for plots

from utils import custom_grid_2d_graph, is_stabilizer, add_stabilizer_to_graph, shift_stabilizer

####################################################

def launch_interactive_composer():
    """Graphical widget for Jupyter notebooks to compose surface code

    The widget is divided into the following tabs:
    tab 0: create grid
    tab 5: save to / load from json (using ConfigFile.toJSON)
    tab 7: clean log
    """
    out = widgets.Output(layout={'border': '1px solid black'})
    outgraph = widgets.Output()
    error_msg = '\033[91mERROR\033[0m:'

    G = custom_grid_2d_graph(1, 1)
    x_ancillas = []
    z_ancillas = []

    # Comments explaining the situation or the meaning of actions.
    label_0 = widgets.Label(value='Add data qubits in a 2D grid:')
    separator = widgets.Label(value='-------------------------')
    msg = 'Add stabilizer in format  "Z(0,0).Z(0,2).Z(2,0).Z(2,2)"  or  "X(0,0).X(0,2)" ' \
          'with shift in format   "(2,2)"  .'
    label_0b = widgets.Label(value=msg)
    msg = 'For example, Z(0,2).Z(0,4) with shift (4,4) equals Z(4,6).Z(4,8)'
    label_0c = widgets.Label(value=msg)
    label_1 = widgets.Label(value='Visualization of the architecture as a directed graph.\nNodes are qubits and directed edges are possible 2-qubit interactions.')
    label_2a = widgets.Label(value='Is the current platform compatible with architectural constraints?')
    label_2b = widgets.Label(value='Save platform to file in JSON format.')

    # Button to click to execute opearation.
    button_0 = widgets.Button(description='ADD DATA QUBITS', layout=widgets.Layout(width='30%', height='40px', border='5px dashed blue'))
    button_0b = widgets.Button(description='ADD STABILIZERS', layout=widgets.Layout(width='30%', height='40px', border='5px dashed blue'))
    button_1 = widgets.Button(description='PLOT GRAPH', layout=widgets.Layout(width='30%', height='40px', border='5px dashed blue'))
    button_2a = widgets.Button(description='CHECK COMPATIBILITY', layout=widgets.Layout(width='30%', height='40px', border='5px dashed green'))
    button_2b = widgets.Button(description='EXPORT TO JSON', layout=widgets.Layout(width='30%', height='40px', border='5px dashed blue'))

    # Numerical variables set by the user.
    nrows = widgets.IntText(value=3, description='num rows:', disabled=False)
    ncols = widgets.IntText(value=3, description='num cols:', disabled=False)
    stab = widgets.Text(value='', description='stabilizer:', disabled=False)
    shift = widgets.Text(value='', description='shift:', disabled=False)

    @button_0.on_click
    @out.capture()
    def func0(button_0):
        nonlocal G
        G = custom_grid_2d_graph(nrows.value, ncols.value)
        out.clear_output() # clear log
        outgraph.clear_output() # clear graph drawing
        button_1.click()

    @button_0b.on_click
    @out.capture()
    def func0(button_0b):
        nonlocal G, x_ancillas, z_ancillas
        # Confirm type of stabilizer.
        is_x_type = is_stabilizer(stab.value, ['x', 'X'])
        is_z_type = is_stabilizer(stab.value, ['z', 'Z'])
        if shift.value != '':
            stabilizer = shift_stabilizer(stab.value, shift.value) 
        else:
            stabilizer = stab.value
        if (is_x_type or is_z_type) == False:
            print(f'stabilizer {stabilizer} is not compatible --> NOT ADDED')
            return

        G, ancilla = add_stabilizer_to_graph(G, stabilizer)
        if is_x_type:
            print(f'stabilizer {stabilizer} is of X-type --> ADDED')
            x_ancillas.append(ancilla)
        elif is_z_type:
            z_ancillas.append(ancilla)
            print(f'stabilizer {stabilizer} is of Z-type --> ADDED')
        button_1.click()

    @button_1.on_click
    @outgraph.capture()
    def func1(button_1):
        outgraph.clear_output()
        nonlocal G
        print('nodes =', G.nodes, '\nedges =', G.edges)
        #pos = nx.spring_layout(G, iterations=100, seed=39775)
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
        if False:
            pos = nx.shell_layout(G)
            nx.draw(G, pos, **options)
        else:
            pos = nx.nx_agraph.graphviz_layout(G, prog="neato")
            nx.draw_networkx(G, pos=pos, **options)
        plt.show()

    @button_2a.on_click
    @out.capture()
    def func1a(button_2a):
        print('TODO: implement the stabilizers-compatibility function')
        if True:
            print('platform is compatible with current architectural constraints')
        else:
            print(error_msg, 'platform is NOT compatible with current architectural constraints')
    
    @button_2b.on_click
    @out.capture()
    def func1b(button_2b):
        filename = 'TEMP.json'
        try:
            file = open(filename, 'w')
            #file.write(platform_.toJSON())
            print('TODO: implement the saving-to-file function')
            file.close()
            print('platform saved in JSON format as \033[94m\033[1m{}\033[0m'.format(filename))
        except IOError:
            print('ERROR: file \033[91m\033[1m{}\033[0m cannot be written (check its path)'.format(filename))

    tab0 = widgets.VBox(children=[label_0, nrows, ncols, button_0, separator, label_0b, label_0c, stab, shift, button_0b])
    tab1 = widgets.VBox(children=[label_1, button_1, ])
    tab2 = widgets.VBox(children=[label_2a, button_2a, label_2b, button_2b, ])

    tab = widgets.Tab(children=[tab0, tab1, tab2])
    tab.set_title(0, 'qubits and stabilizers')
    tab.set_title(1, 'plot qubits')
    tab.set_title(2, 'export to json')

    return widgets.VBox(children=[tab, out, outgraph])

####################################################
