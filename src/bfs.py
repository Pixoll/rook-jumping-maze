from queue import SimpleQueue

from src.graph import Graph, Node


def bfs(graph: Graph) -> list[Node] | None:
    visited: set[tuple[int, int]] = {graph.root.pos}
    queue: SimpleQueue[Node] = SimpleQueue()
    queue.put(graph.root)
    parent: dict[tuple[int, int], Node | None] = {graph.root.pos: None}
    goal: Node | None = None

    while not queue.empty():
        node = queue.get()

        if node.is_goal:
            goal = node
            break

        for edge in node.edges:
            neighbour = edge.dest

            if neighbour.pos not in visited:
                visited.add(neighbour.pos)
                parent[neighbour.pos] = node
                queue.put(neighbour)

    if goal is None:
        return None

    path: list[Node] = []
    current = goal

    while current is not None:
        path.append(current)
        current = parent[current.pos]

    return path[::-1]
