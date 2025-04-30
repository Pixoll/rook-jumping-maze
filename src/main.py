from pathlib import Path

from graph import Graph, Node
from visualizer import PathfindingVisualizer


def main() -> None:
    root_path = Path(__file__).parent.parent.resolve()
    input_path = root_path / "input.txt"
    lines: list[str] = []

    with open(input_path) as input_file:
        lines += input_file.read().splitlines()

    line_index = 0
    graphs: list[Graph] = []

    while line_index < len(lines) and lines[line_index].strip() != "0":
        rows, cols, start_i, start_j, goal_i, goal_j = map(int, lines[line_index].split())
        line_index += 1
        matrix: list[list[int]] = []

        for i in range(rows):
            values = list(map(int, lines[line_index].split()))
            if len(values) != cols:
                raise Exception(f"Expected {cols} columns in line {line_index}")

            matrix.append(values)
            line_index += 1

        graph = Graph(matrix, (start_i, start_j), (goal_i, goal_j))
        graphs.append(graph)

        print(graph)
        print()
        print_results(graph, ["dfs", "ucs_by_distance", "ucs_by_jumps", "ucs_by_value", "bfs", "dijkstra", "a_star"])
        print()

    if len(graphs) == 0:
        raise Exception("No graphs found")

    visualizer = PathfindingVisualizer(graphs)
    visualizer.run()
    visualizer.quit()


def print_results(graph: Graph, method_names: list[str], coords_only: bool = True) -> None:
    max_length = max([len(name) for name in method_names])

    for name in method_names:
        if not hasattr(graph, name):
            raise Exception(f"Method Graph.{name}() not found")

        method = getattr(graph, name)

        if not callable(method):
            raise Exception(f"Method Graph.{name}() not found")

        padded_name = name.ljust(max_length, " ")
        result: list[Node] | None = method()

        size = len(result) - 1 if result is not None else 0
        result_list = list(map(lambda n: n.pos, result)) if coords_only and result is not None else result
        print(f"{padded_name} : {{{size}}}{result_list}")


if __name__ == '__main__':
    main()
