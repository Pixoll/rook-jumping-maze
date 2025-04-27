from queue import PriorityQueue, SimpleQueue


class Node:
    edges: list['Edge']
    is_goal: bool

    def __init__(self, pos: tuple[int, int], is_goal: bool = False) -> None:
        self.pos = pos
        self.is_goal = is_goal
        self.edges = []

    # for PriorityQueue, do not remove
    def __lt__(self, other: 'Node') -> bool:
        return self.pos < other.pos

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
    _nodes: set[Node]
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
        self._start = start
        self._goal = goal

        for i, row in enumerate(matrix):
            for j, length in enumerate(row):
                pos = (i, j)
                node = self._nodes[pos] if pos in self._nodes else Node(pos, pos == goal)
                self._nodes[pos] = node

                if length == 0:
                    continue

                for di, dj in ((-length, 0), (length, 0), (0, -length), (0, length)):
                    ni = pos[0] + di
                    nj = pos[1] + dj
                    n_pos = (ni, nj)

                    if 0 <= ni < len(matrix) and 0 <= nj < len(row):
                        neighbour = self._nodes[n_pos] if n_pos in self._nodes else Node(n_pos, n_pos == goal)
                        self._nodes[n_pos] = neighbour
                        edge = Edge(
                            neighbour,
                            length,
                            heuristics[ni][nj] if heuristics is not None else 0
                        )
                        node.edges.append(edge)

        self._root = self._nodes[self._start]

    def bfs(self) -> list[Node] | None:
        visited: set[tuple[int, int]] = {self._root.pos}
        parents: dict[tuple[int, int], Node | None] = {self._root.pos: None}
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

                if neighbour.pos not in visited:
                    visited.add(neighbour.pos)
                    parents[neighbour.pos] = node
                    queue.put(neighbour)

        return self._get_path(parents, goal)

    def dfs(self) -> list[Node] | None:
        visited: set[tuple[int, int]] = set()
        parents: dict[tuple[int, int], Node | None] = {self._root.pos: None}
        goal: Node | None = None

        stack = [self._root]

        while len(stack) > 0:
            node = stack.pop()

            if node.is_goal:
                goal = node
                break

            if node.pos not in visited:
                visited.add(node.pos)

                for edge in reversed(node.edges):
                    neighbour = edge.dest

                    if neighbour.pos not in visited:
                        stack.append(neighbour)

                        if neighbour.pos not in parents:
                            parents[neighbour.pos] = node

        return self._get_path(parents, goal)

    def ucs(self) -> list[Node] | None:
        visited: set[tuple[int, int]] = set()
        final_path: list[Node] | None = None

        pq: PriorityQueue[tuple[int, Node, list[Node]]] = PriorityQueue()
        pq.put((0, self._root, [self._root]))

        while not pq.empty():
            cumulative, node, path = pq.get()
            visited.add(node.pos)

            if node.is_goal:
                final_path = path
                break

            for edge in node.edges:
                neighbour = edge.dest

                if neighbour.pos not in visited:
                    pq.put((cumulative + edge.length, neighbour, path + [neighbour]))

        return final_path

    @staticmethod
    def _get_path(parents: dict[tuple[int, int], Node | None], goal: Node | None) -> list[Node] | None:
        if goal is None:
            return None

        path: list[Node] = []
        current = goal

        while current is not None:
            path.append(current)
            current = parents[current.pos]

        return path[::-1]
