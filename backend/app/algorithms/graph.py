Graph = dict[int, list[int]]


# Cycle detection
# Edges point from a movie to its prerequisites.
# Giving movie_id new prerequisites makes a cycle only if movie_id
# can already be reached from one of those prerequisites.

def find_cycle(graph: Graph, movie_id: int, new_prerequisite_ids: list[int]) -> list[int] | None:
    parent: dict[int, int] = {}
    visited: set[int] = set()
    stack: list[int] = []

    for start in new_prerequisite_ids:
        if start not in visited:
            visited.add(start)
            parent[start] = movie_id
            stack.append(start)

    while stack:
        current = stack.pop()
        if current == movie_id:
            return _build_cycle_path(parent, movie_id)
        for next_id in graph.get(current, []):
            if next_id not in visited:
                visited.add(next_id)
                parent[next_id] = current
                stack.append(next_id)

    return None


def _build_cycle_path(parent: dict[int, int], movie_id: int) -> list[int]:
    path = [movie_id]
    node = parent[movie_id]
    while node != movie_id:
        path.append(node)
        node = parent[node]
    path.append(movie_id)
    path.reverse()
    return path
# Rewatch order (topological sort with DFS post-order)
# A movie is added only after all of its prerequisites are added.
def rewatch_order(graph: Graph, target_id: int) -> list[int]:
    order: list[int] = []
    visited: set[int] = {target_id}
    def visit(movie_id: int) -> None:
        visited.add(movie_id)
        for prerequisite_id in graph.get(movie_id, []):
            if prerequisite_id not in visited:
                visit(prerequisite_id)
        order.append(movie_id)
    for prerequisite_id in graph.get(target_id, []):
        if prerequisite_id not in visited:
            visit(prerequisite_id)
    return order
