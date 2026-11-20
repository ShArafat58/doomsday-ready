import pytest
from app.algorithms.booking import fewest_bundles
def seats(result: dict[int, int]) -> int:
    return sum(size * count for size, count in result.items())
# Task examples
@pytest.mark.parametrize(
    "sizes, group_size, expected",
    [
        ([1, 3, 4], 6, {3: 2}),
        ([2, 5], 11, {5: 1, 2: 3}),
        ([6, 9, 20], 44, {20: 1, 9: 2, 6: 1}),
    ],
)
def test_task_examples(sizes, group_size, expected):
    assert fewest_bundles(sizes, group_size) == expected
def test_not_possible_returns_none():
    assert fewest_bundles([4, 6], 7) is None
# Edge cases
def test_dp_beats_greedy():
    result = fewest_bundles([1, 5, 6, 9], 11)
    assert sum(result.values()) == 2
    assert seats(result) == 11
def test_single_bundle_that_fits_exactly():
    assert fewest_bundles([7], 7) == {7: 1}
def test_largest_group_size():
    result = fewest_bundles([6, 9, 20], 10000)
    assert seats(result) == 10000
    assert sum(result.values()) == 500
def test_every_answer_adds_up_exactly():
    for group_size in range(1, 201):
        result = fewest_bundles([4, 6, 9], group_size)
        if result is not None:
            assert seats(result) == group_size
