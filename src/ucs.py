from queue import PriorityQueue

from src.graph import Graph, Node


def ucs(graph: Graph) -> list[Node] | None:
    visited: set[tuple[int, int]] = set()

    pq: PriorityQueue[tuple[int, Node, list[Node]]] = PriorityQueue()
    pq.put((0, graph.root, [graph.root]))

    final_path: list[Node] | None = None

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
