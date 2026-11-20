# Fewest bundles (dynamic programming, like the coin change problem)
# best[s] is the fewest bundles that give exactly s seats.
# last[s] is the bundle size used last to reach s, used to rebuild the answer.
def fewest_bundles(bundle_sizes: list[int], group_size: int) -> dict[int, int] | None:
    impossible = group_size + 1
    best = [0] + [impossible] * group_size
    last = [0] * (group_size + 1)
    sizes = sorted(bundle_sizes, reverse=True)
    for seats in range(1, group_size + 1):
        for size in sizes:
            if size <= seats and best[seats - size] + 1 < best[seats]:
                best[seats] = best[seats - size] + 1
                last[seats] = size
    if best[group_size] == impossible:
        return None
    counts: dict[int, int] = {}
    seats = group_size
    while seats > 0:
        size = last[seats]
        counts[size] = counts.get(size, 0) + 1
        seats -= size
    return counts
