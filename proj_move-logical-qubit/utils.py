"""Utility functions to create the abstract representation of logical qubit movement

We adopt a representation at the plaquette level, representing each plaquette type
via an integer code. The plaquette type are unique based on:
- if they are an X or Z stabilizer
- if they have support on 2 or 4 qubits
- the order of data qubits involved in a 2q gate in the circuit
implementing the stabilizer measurement
"""

import numpy as np
from typing import List, Tuple, Dict
from ast import literal_eval

####################################################

def move_L_shape(distance: int, v_shift: int, h_shift: int, resize_to_distance: int = 0) -> List:
    """Return plaquette arrangement as a 2d grid"""
    if resize_to_distance == 0:
        resize_to_distance = distance
    else:
        raise NotImplementedError('only move without resize (at present)')
    
    if distance%2==0 or resize_to_distance%2==0:
        raise ValueError('code distance must be an odd integer')
    if v_shift%2==1 or h_shift%2==1:
        raise ValueError('shifts must be even integers')
    if v_shift < resize_to_distance or h_shift < resize_to_distance:
        raise ValueError('shifts must be larger than code distance')
    
    # Create 2d grid large enough for all plaquettes (boundary included).
    v_dim = distance-1 + v_shift + 2
    h_dim = distance-1 + h_shift + 2
    arrang = np.zeros((v_dim, h_dim), dtype=int)

    # Initial position of logical qubit and vertical shift.
    for v in range(1, distance + v_shift):
        for h in range(1, distance):
            if h > distance+v_shift-v-1:
                continue
            if (v+h)%2==0:
                arrang[v][h] = 3
            else:
                arrang[v][h] = 4
    # Final position of logical qubit and horizontal shift.
    for v in range(v_shift+1, distance + v_shift):
        for h in range(1, distance + h_shift):
            if h < distance+v_shift-v:
                continue
            if (v+h)%2==0:
                arrang[v][h] = 9
            else:
                arrang[v][h] = 8
    # Complete corner.
    arrang[-2][1] = 11
    arrang[-1-distance][distance] = 6
    # Add boundaries.
    for v in range(v_dim):
        for h in range(h_dim):
            if arrang[v][h] != 0:
                continue
            # Left boundary
            if h+1 < h_dim and arrang[v][h+1]==3:
                arrang[v][h] = 2
            elif h+1 < h_dim and arrang[v][h+1]==8:
                arrang[v][h] = 14
            # Right boundary
            if h > 0 and arrang[v][h-1]==3:
                arrang[v][h] = 5
            elif h > 0 and arrang[v][h-1]==8:
                arrang[v][h] = 10
            # Top boundary
            if v+1 < v_dim and arrang[v+1][h]==4:
                arrang[v][h] = 1
            elif v+1 < v_dim and arrang[v+1][h]==9:
                arrang[v][h] = 7
            # Bottom boundary
            if v > 0 and arrang[v-1][h]==9:
                arrang[v][h] = 12
            elif v > 0 and arrang[v-1][h]==4:
                arrang[v][h] = 13
    return arrang

####################################################

def visualize_plaquettes(arrangement: List, nopl: str = " ."):
    """Visualize plaquette arrangement"""
    for row in arrangement:
        for p in row:
            if p == 0:
                print(nopl, end=' ')
            else:
                print(f'{p:2.0f}', end=' ')
        print()
    return

####################################################
