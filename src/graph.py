from collections.abc import Callable
from math import inf
from queue import PriorityQueue, SimpleQueue


class Node:
    pos: tuple[int, int]
    value: int
    heuristic: int
    is_goal: bool
    edges: list['Edge']

    def __init__(self, pos: tuple[int, int], value: int, goal: tuple[int, int], max_jump: int) -> None:
        self.pos = pos
        self.value = value
        self.heuristic = (abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])) // (max_jump - 1)
        self.is_goal = pos == goal
        self.edges = []

    # for PriorityQueue, do not remove
    def __lt__(self, other: 'Node') -> bool:
        return True

    def __str__(self) -> str:
        return str(self.pos)

    def __repr__(self) -> str:
        return f'Node({self.pos}, {self.is_goal})'


class Edge:
    def __init__(self, dest: Node, length: int) -> None:
        self.dest = dest
        self.length = length

    def __str__(self) -> str:
        return str((self.dest, self.length))

    def __repr__(self) -> str:
        return f'Edge({self.dest}, {self.length})'


class Graph:
    nodes: set[Node]
    matrix: list[list[int]]
    start: tuple[int, int]
    _goal: tuple[int, int]
    _root: Node

    def __init__(self, matrix: list[list[int]], start: tuple[int, int], goal: tuple[int, int]) -> None:
        self.nodes: dict[tuple[int, int], Node] = dict()
        self.matrix = matrix
        self.start = start
        self._goal = goal
        max_jump = max([max(row) for row in matrix])

        for i, row in enumerate(matrix):
            for j, length in enumerate(row):
                pos = (i, j)
                node = self.nodes[pos] if pos in self.nodes else Node(pos, matrix[i][j], goal, max_jump)
                self.nodes[pos] = node

                if length == 0:
                    continue

                for di, dj in ((-length, 0), (length, 0), (0, -length), (0, length)):
                    ni = pos[0] + di
                    nj = pos[1] + dj
                    n_pos = (ni, nj)

                    if 0 <= ni < len(matrix) and 0 <= nj < len(row):
                        neighbour = (self.nodes[n_pos] if n_pos in self.nodes
                                     else Node(n_pos, matrix[ni][nj], goal, max_jump))
                        self.nodes[n_pos] = neighbour
                        edge = Edge(neighbour, length)
                        node.edges.append(edge)

        self._root = self.nodes[self.start]

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

    def bfs(self) -> list[Node] | None:
        visited: set[Node] = {self._root}
        parents: dict[Node, Node | None] = {self._root: None}
        goal: Node | None = None

        queue: SimpleQueue[Node] = SimpleQueue()
        queue.put(self._root)

        while not queue.empty():
            node = queue.get()

            if node.is_goal:
                goal = node
                break

            for edge in node.edges:
                neighbour = edge.dest

                if neighbour not in visited:
                    visited.add(neighbour)
                    parents[neighbour] = node
                    queue.put(neighbour)

        return self._get_path(parents, goal)

    def dijkstra(self) -> list[Node] | None:
        distances: dict[Node, float] = {self._root: 0}
        parents: dict[Node, Node | None] = {self._root: None}
        goal: Node | None = None

        pq: PriorityQueue[tuple[float, Node]] = PriorityQueue()
        pq.put((0, self._root))

        for node in self.nodes.values():
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
        visited: set[Node] = set()
        g_scores: dict[Node, float] = {self._root: 0}
        f_scores: dict[Node, float] = {self._root: self._root.heuristic}

        parents: dict[Node, Node | None] = {self._root: None}
        goal: Node | None = None

        pq: PriorityQueue[tuple[float, Node]] = PriorityQueue()
        pq.put((0, self._root))

        while not pq.empty():
            _, node = pq.get()

            if node in visited:
                continue

            if node.is_goal:
                goal = node
                break

            visited.add(node)

            for edge in node.edges:
                neighbour = edge.dest
                tentative_g_score = g_scores[node] + edge.length

                if neighbour not in g_scores or tentative_g_score < g_scores[neighbour]:
                    parents[neighbour] = node
                    g_scores[neighbour] = tentative_g_score
                    f_scores[neighbour] = tentative_g_score + neighbour.heuristic
                    pq.put((f_scores[neighbour], neighbour))

        return self._get_path(parents, goal)

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

    def __repr__(self) -> str:
        header = f"Graph({len(self.matrix)}x{len(self.matrix[0])}, {self.start} -> {self._goal}):"
        value_length = max(map(lambda node: node.value // 10 + 1, self.nodes.values()))
        matrix = "\n".join(map(
            lambda row: " ".join([("G" if v == 0 else str(v)).rjust(value_length, " ") for v in row]),
            self.matrix
        ))
        return header + "\n" + matrix
