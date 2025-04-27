from queue import PriorityQueue

from src.graph import Graph, Node


def ucs(graph: Graph) -> list[tuple[int, int]] | None:
    visited: set[tuple[int, int]] = set()

    pq: PriorityQueue[tuple[int, Node, list[tuple[int, int]]]] = PriorityQueue()
    pq.put((0, graph.root, [graph.root.pos]))

    final_path: list[tuple[int, int]] | None = None

    while not pq.empty():
        cumulative, node, path = pq.get()
        visited.add(node.pos)

        if node.is_goal:
            final_path = path
            break

        for edge in node.edges:
            neighbour = edge.dest
            distance = cumulative + edge.length
            new_path = path + [neighbour.pos]

            if neighbour.is_goal:
                final_path = new_path
                break

            if neighbour.pos not in visited:
                pq.put((distance, neighbour, new_path))

    return final_path
