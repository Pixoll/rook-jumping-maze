from pathlib import Path

from src.graph import Graph


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
        dfs_result = graph.dfs()
        ucs_result = graph.ucs()
        bfs_result = graph.bfs()

        print(f"dfs(graph) = {{{len(dfs_result) - 1 if dfs_result is not None else 0}}}{dfs_result}")
        print(f"usc(graph) = {{{len(ucs_result) - 1 if ucs_result is not None else 0}}}{ucs_result}")
        print(f"bfs(graph) = {{{len(bfs_result) - 1 if bfs_result is not None else 0}}}{bfs_result}")


if __name__ == '__main__':
    main()
