class Node:
    edges: list['Edge']
    is_goal: bool

    def __init__(self, pos: tuple[int, int], is_goal: bool = False) -> None:
        self.pos = pos
        self.is_goal = is_goal
        self.edges = []

    def __str__(self) -> str:
        return str(self.pos)

    def __repr__(self) -> str:
        return f'Node({self.pos}, {self.is_goal})'


class Edge:
    def __init__(self, dest: Node, length: int, heuristic: int = 0) -> None:
        self.dest = dest
        self.length = length
        self.heuristic = heuristic

    def __str__(self) -> str:
        return str((self.dest, self.length, self.heuristic))

    def __repr__(self) -> str:
        return f'Edge({self.dest}, {self.length}, {self.heuristic})'


class Graph:
    nodes: set[Node]
    start: tuple[int, int]
    goal: tuple[int, int]

    def __init__(
            self,
            matrix: list[list[int]],
            start: tuple[int, int],
            goal: tuple[int, int],
            heuristics: list[list[int]] | None = None,
    ) -> None:
        self.nodes: dict[tuple[int, int], Node] = dict()
        self.start = start
        self.goal = goal

        for i, row in enumerate(matrix):
            for j, length in enumerate(row):
                pos = (i, j)
                node = self.nodes[pos] if pos in self.nodes else Node(pos, pos == goal)
                self.nodes[pos] = node

                if length == 0:
                    continue

                for di, dj in ((-length, 0), (length, 0), (0, -length), (0, length)):
                    ni = pos[0] + di
                    nj = pos[1] + dj
                    n_pos = (ni, nj)

                    if 0 <= ni < len(matrix) and 0 <= nj < len(row):
                        neighbour = self.nodes[n_pos] if n_pos in self.nodes else Node(n_pos, n_pos == goal)
                        self.nodes[n_pos] = neighbour
                        edge = Edge(
                            neighbour,
                            length,
                            heuristics[ni][nj] if heuristics is not None else 0
                        )
                        node.edges.append(edge)

    @property
    def root(self) -> Node:
        return self.nodes[self.start]
