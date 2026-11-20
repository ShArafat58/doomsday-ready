from sqlalchemy.orm import Session
from app.algorithms.graph import rewatch_order
from app.schemas import RewatchPlan
from app.services.movies import get_movie, list_movies, load_graph, to_read
# Rewatch plan: stable order (older movies first), then the counts
def get_rewatch_plan(db: Session, movie_id: int) -> RewatchPlan:
    target = get_movie(db, movie_id)
    movies = {m.id: m for m in list_movies(db)}
    graph = load_graph(db)
    for prerequisite_ids in graph.values():
        prerequisite_ids.sort(key=lambda i: (movies[i].release_year, movies[i].title))
    plan = [to_read(movies[i]) for i in rewatch_order(graph, target.id)]
    return RewatchPlan(
        target=to_read(target),
        movies=plan,
        total_count=len(plan),
        watched_count=sum(1 for m in plan if m.watched),
        unwatched_runtime_minutes=sum(m.runtime_minutes for m in plan if not m.watched),
    )
