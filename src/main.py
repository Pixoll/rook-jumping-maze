from pathlib import Path

from src.graph import Graph, Node


def main() -> None:
    root_path = Path(__file__).parent.parent.resolve()
    input_path = root_path / "input.txt"
    lines: list[str] = []

    with open(input_path) as input_file:
        lines += input_file.read().splitlines()

    line_index = 0

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

        print(graph)
        print()
        print_result("dfs", graph.dfs())
        print_result("ucs_by_distance", graph.ucs_by_distance())
        print_result("ucs_by_jumps", graph.ucs_by_jumps())
        print_result("ucs_by_value", graph.ucs_by_value())
        print_result("dijkstra", graph.dijkstra())
        print()


def print_result(name: str, result: list[Node] | None, coords_only: bool = True) -> None:
    size = len(result) - 1 if result is not None else 0
    result_list = list(map(lambda n: n.pos, result)) if coords_only and result is not None else result
    print(f"{name}: {{{size}}}{result_list}")


if __name__ == '__main__':
    main()
