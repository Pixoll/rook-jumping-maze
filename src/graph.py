from collections.abc import Callable
from math import inf
from queue import PriorityQueue


class Node:
    pos: tuple[int, int]
    value: int
    is_goal: bool
    edges: list['Edge']

    def __init__(self, pos: tuple[int, int], value: int, is_goal: bool = False) -> None:
        self.pos = pos
        self.value = value
        self.is_goal = is_goal
        self.edges = []

    # for PriorityQueue, do not remove
    def __lt__(self, other: 'Node') -> bool:
        return True

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
        return f'Edge({self.dest}, g={self.length}, h={self.heuristic})'


class Graph:
    _nodes: set[Node]
    _matrix: list[list[int]]
    _start: tuple[int, int]
    _goal: tuple[int, int]
    _root: Node

    def __init__(
            self,
            matrix: list[list[int]],
            start: tuple[int, int],
            goal: tuple[int, int],
            heuristics: list[list[int]] | None = None,
    ) -> None:
        self._nodes: dict[tuple[int, int], Node] = dict()
        self._matrix = matrix
        self._start = start
        self._goal = goal

        for i, row in enumerate(matrix):
            for j, length in enumerate(row):
                pos = (i, j)
                node = self._nodes[pos] if pos in self._nodes else Node(pos, matrix[i][j], pos == goal)
                self._nodes[pos] = node

                if length == 0:
                    continue

                for di, dj in ((-length, 0), (length, 0), (0, -length), (0, length)):
                    ni = pos[0] + di
                    nj = pos[1] + dj
                    n_pos = (ni, nj)

                    if 0 <= ni < len(matrix) and 0 <= nj < len(row):
                        neighbour = (self._nodes[n_pos] if n_pos in self._nodes
                                     else Node(n_pos, matrix[ni][nj], n_pos == goal))
                        self._nodes[n_pos] = neighbour
                        edge = Edge(
                            neighbour,
                            length,
                            heuristics[ni][nj] if heuristics is not None else 0
                        )
                        node.edges.append(edge)

        self._root = self._nodes[self._start]

    def dfs(self) -> list[Node] | None:
        visited: set[Node] = set()
        parents: dict[Node, Node | None] = {self._root: None}
        goal: Node | None = None

        stack = [self._root]

        while len(stack) > 0:
            node = stack.pop()

            if node.is_goal:
                goal = node
                break

            if node not in visited:
                visited.add(node)

                for edge in reversed(node.edges):
                    neighbour = edge.dest

                    if neighbour not in visited:
                        stack.append(neighbour)

                        if neighbour not in parents:
                            parents[neighbour] = node

        return self._get_path(parents, goal)

    def ucs_by_distance(self) -> list[Node] | None:
        return self._ucs(lambda edge: edge.length)

    def ucs_by_jumps(self) -> list[Node] | None:
        return self._ucs(lambda _: 1)

    def ucs_by_value(self) -> list[Node] | None:
        return self._ucs(lambda edge: edge.dest.value)

    def dijkstra(self) -> list[Node] | None:
        distances: dict[Node, float] = {self._root: 0}
        parents: dict[Node, Node | None] = {self._root: None}
        goal: Node | None = None

        pq: PriorityQueue[tuple[float, Node]] = PriorityQueue()
        pq.put((0, self._root))

        for node in self._nodes.values():
            if node != self._root:
                parents[node] = None
                distances[node] = inf
                pq.put((inf, node))

        while not pq.empty():
            distance, node = pq.get()

            if node.is_goal:
                goal = node
                break

            for edge in node.edges:
                neighbour = edge.dest
                new_distance = distances[node] + edge.length

                if new_distance < distances[neighbour]:
                    parents[neighbour] = node
                    distances[neighbour] = new_distance
                    pq.put((new_distance, neighbour))

        return self._get_path(parents, goal)

    def a_star(self) -> list[Node] | None:
        g_scores: dict[Node, float] = {self._root: 0}
        f_scores: dict[Node, float] = {self._root: 0}

        parents: dict[Node, Node | None] = {self._root: None}
        goal: Node | None = None

        pq: PriorityQueue[tuple[float, Node]] = PriorityQueue()
        pq.put((0, self._root))

        while not pq.empty():
            g_score, node = pq.get()

            if node.is_goal:
                goal = node
                break

            for edge in node.edges:
                neighbour = edge.dest
                tentative_g_score = g_score + edge.length

                if neighbour not in g_scores or tentative_g_score < g_scores[neighbour]:
                    parents[neighbour] = node
                    g_scores[neighbour] = tentative_g_score
                    f_scores[neighbour] = tentative_g_score + edge.heuristic
                    pq.put((tentative_g_score, neighbour))

        return self._get_path(parents, goal)

    def __repr__(self) -> str:
        header = f"Graph({len(self._matrix)}x{len(self._matrix[0])}, {self._start} -> {self._goal}):"
        matrix = "\n".join(map(lambda row: " ".join(["G" if v == 0 else str(v) for v in row]), self._matrix))
        return header + "\n" + matrix

    def _ucs(self, increment: Callable[[Edge], int]) -> list[Node] | None:
        visited: set[Node] = set()
        final_path: list[Node] | None = None

        pq: PriorityQueue[tuple[int, Node, list[Node]]] = PriorityQueue()
        pq.put((0, self._root, [self._root]))

        while not pq.empty():
            total, node, path = pq.get()
            visited.add(node)

            if node.is_goal:
                final_path = path
                break

            for edge in node.edges:
                neighbour = edge.dest

                if neighbour not in visited:
                    pq.put((total + increment(edge), neighbour, path + [neighbour]))

        return final_path

    @staticmethod
    def _get_path(parents: dict[Node, Node | None], goal: Node | None) -> list[Node] | None:
        if goal is None or parents[goal] is None:
            return None

        path: list[Node] = []
        current = goal

        while current is not None:
            path.append(current)
            current = parents[current]

        return path[::-1]
