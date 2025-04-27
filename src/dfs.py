from src.graph import Graph, Node


def dfs(graph: Graph) -> list[Node] | None:
    visited: set[tuple[int, int]] = set()
    stack = [graph.root]
    parent: dict[tuple[int, int], Node | None] = {graph.root.pos: None}
    goal: Node | None = None

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

                    if neighbour.pos not in parent:
                        parent[neighbour.pos] = node

    if goal is None:
        return None

    path: list[Node] = []
    current = goal

    while current is not None:
        path.append(current)
        current = parent[current.pos]

    return path[::-1]
