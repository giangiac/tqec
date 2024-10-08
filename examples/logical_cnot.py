"""This is an example of compiling a logical CNOT `.dae` model to
`stim.Circuit`."""

import itertools
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import sinter
import stim

from tqec import (
    BlockGraph,
    Position3D,
    ZXGraph,
    annotate_detectors_automatically,
    compile_block_graph,
)
from tqec.compile.compile import CompiledGraph
from tqec.noise_models import NoiseModel

EXAMPLE_FOLDER = Path(__file__).parent
TQEC_FOLDER = EXAMPLE_FOLDER.parent
ASSETS_FOLDER = TQEC_FOLDER / "assets"
CNOT_DAE_FILE = ASSETS_FOLDER / "logical_cnot.dae"


def create_block_graph(from_scratch: bool = False) -> BlockGraph:
    if not from_scratch:
        return BlockGraph.from_dae_file(CNOT_DAE_FILE)

    cnot_zx = ZXGraph("Logical CNOT ZX Graph")

    cnot_zx.add_z_node(Position3D(0, 0, 0))
    cnot_zx.add_x_node(Position3D(0, 0, 1))
    cnot_zx.add_z_node(Position3D(0, 0, 2))
    cnot_zx.add_z_node(Position3D(0, 0, 3))
    cnot_zx.add_x_node(Position3D(0, 1, 1))
    cnot_zx.add_z_node(Position3D(0, 1, 2))
    cnot_zx.add_z_node(Position3D(1, 1, 0))
    cnot_zx.add_z_node(Position3D(1, 1, 1))
    cnot_zx.add_z_node(Position3D(1, 1, 2))
    cnot_zx.add_z_node(Position3D(1, 1, 3))

    cnot_zx.add_edge(Position3D(0, 0, 0), Position3D(0, 0, 1))
    cnot_zx.add_edge(Position3D(0, 0, 1), Position3D(0, 0, 2))
    cnot_zx.add_edge(Position3D(0, 0, 2), Position3D(0, 0, 3))
    cnot_zx.add_edge(Position3D(0, 0, 1), Position3D(0, 1, 1))
    cnot_zx.add_edge(Position3D(0, 1, 1), Position3D(0, 1, 2))
    cnot_zx.add_edge(Position3D(0, 1, 2), Position3D(1, 1, 2))
    cnot_zx.add_edge(Position3D(1, 1, 0), Position3D(1, 1, 1))
    cnot_zx.add_edge(Position3D(1, 1, 1), Position3D(1, 1, 2))
    cnot_zx.add_edge(Position3D(1, 1, 2), Position3D(1, 1, 3))
    return cnot_zx.to_block_graph("Logical CNOT Block Graph")


def generate_stim_circuit(
    compiled_graph: CompiledGraph, k: int, p: float
) -> stim.Circuit:
    circuit_without_detectors = compiled_graph.generate_stim_circuit(
        k,
        noise_model=NoiseModel.uniform_depolarizing(p),
    )
    # For now, we annotate the detectors as post-processing step
    return annotate_detectors_automatically(circuit_without_detectors)


def get_sinter_task(
    compiled_graph: CompiledGraph, tup: tuple[int, float]
) -> sinter.Task:
    k, p = tup
    return sinter.Task(
        circuit=generate_stim_circuit(compiled_graph, k, p),
        json_metadata={"d": 2 * k + 1, "r": 2 * k + 1, "p": p},
    )


def main() -> None:
    # 1 Create `BlockGraph` representing the computation
    block_graph = create_block_graph(from_scratch=False)

    # 2. (Optional) Find and choose the logical observables
    observables = block_graph.get_abstract_observables()

    # 3. Compile the `BlockGraph`
    # NOTE:that the scalable detector automation approach is still work in process.
    compiled_graph = compile_block_graph(
        block_graph,
        observables=[observables[1]],
    )

    _MAX_WORKERS: int = 16

    # 4. Generate `stim.Circuit`s from the compiled graph and run the simulation
    def gen_tasks() -> Iterable[sinter.Task]:
        with ProcessPoolExecutor(max_workers=_MAX_WORKERS) as p:
            yield from p.map(
                get_sinter_task,
                itertools.repeat(compiled_graph),
                itertools.product(
                    range(1, 6),
                    [0.0005, 0.001, 0.004, 0.008, 0.01, 0.012, 0.014, 0.018],
                ),
            )

    stats = sinter.collect(
        num_workers=_MAX_WORKERS,
        tasks=gen_tasks(),
        max_errors=5000,
        max_shots=100_000_000,
        decoders=["pymatching"],
        print_progress=True,
    )
    fig, ax = plt.subplots()
    sinter.plot_error_rate(
        ax=ax,
        stats=stats,
        x_func=lambda stat: stat.json_metadata["p"],
        group_func=lambda stat: stat.json_metadata["d"],
    )
    ax.grid(axis="both")
    ax.legend()
    ax.loglog()
    ax.set_title("Logical CNOT Error Rate")
    fig.savefig(ASSETS_FOLDER / "logical_cnot_result.png")


if __name__ == "__main__":
    main()