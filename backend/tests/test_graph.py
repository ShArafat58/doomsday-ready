from app.algorithms.graph import find_cycle, rewatch_order
IRON_MAN, FIRST_AVENGER, AVENGERS, CIVIL_WAR, RAGNAROK, INFINITY_WAR, ENDGAME, DOOMSDAY = range(1, 9)
# Sample graph from the task: movie -> its prerequisites
GRAPH = {
    AVENGERS: [IRON_MAN, FIRST_AVENGER],
    CIVIL_WAR: [AVENGERS],
    INFINITY_WAR: [CIVIL_WAR, RAGNAROK],
    ENDGAME: [INFINITY_WAR],
    DOOMSDAY: [ENDGAME],
}
def assert_prerequisites_come_first(order, graph):
    position = {movie: i for i, movie in enumerate(order)}
    for movie in order:
        for prerequisite in graph.get(movie, []):
            assert position[prerequisite] < position[movie]
# Rewatch order
def test_doomsday_needs_all_seven_other_movies_in_a_valid_order():
    order = rewatch_order(GRAPH, DOOMSDAY)
    assert sorted(order) == [1, 2, 3, 4, 5, 6, 7]
    assert len(order) == len(set(order))
    assert_prerequisites_come_first(order, GRAPH)
def test_civil_war_needs_iron_man_and_first_avenger_then_avengers():
    order = rewatch_order(GRAPH, CIVIL_WAR)
    assert set(order[:2]) == {IRON_MAN, FIRST_AVENGER}
    assert order[2:] == [AVENGERS]
def test_movie_without_prerequisites_has_empty_order():
    assert rewatch_order(GRAPH, RAGNAROK) == []
def test_shared_prerequisite_appears_only_once():
    diamond = {4: [2, 3], 2: [1], 3: [1]}
    order = rewatch_order(diamond, 4)
    assert order.count(1) == 1
    assert_prerequisites_come_first(order, diamond)
# Cycle detection
def test_endgame_as_prerequisite_of_iron_man_is_a_cycle():
    path = find_cycle(GRAPH, IRON_MAN, [ENDGAME])
    assert path == [IRON_MAN, ENDGAME, INFINITY_WAR, CIVIL_WAR, AVENGERS, IRON_MAN]
def test_movie_as_its_own_prerequisite_is_a_cycle():
    assert find_cycle(GRAPH, IRON_MAN, [IRON_MAN]) == [IRON_MAN, IRON_MAN]
def test_valid_change_has_no_cycle():
    assert find_cycle(GRAPH, DOOMSDAY, [RAGNAROK, IRON_MAN]) is None
