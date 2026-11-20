import { useEffect, useState } from 'react'
import { api, formatRuntime } from '../api'
import type { Movie, RewatchPlan } from '../api'
import Poster from '../Poster'
import { inputClass, labelClass } from '../styles'
import { Card, ErrorBox } from '../ui'
export default function RewatchView() {
  const [movies, setMovies] = useState<Movie[]>([])
  const [targetId, setTargetId] = useState<number | null>(null)
  const [plan, setPlan] = useState<RewatchPlan | null>(null)
  const [error, setError] = useState<unknown>(null)
  useEffect(() => {
    api
      .listMovies()
      .then((list) => {
        setMovies(list)
        const doomsday = list.find((m) => m.title.toLowerCase().includes('doomsday'))
        setTargetId((doomsday ?? list[list.length - 1])?.id ?? null)
      })
      .catch(setError)
  }, [])
  useEffect(() => {
    if (targetId === null) return
    api
      .rewatchOrder(targetId)
      .then((result) => {
        setPlan(result)
        setError(null)
      })
      .catch(setError)
  }, [targetId])
  async function toggleWatched(movie: Movie) {
    try {
      await api.updateMovie(movie.id, { watched: !movie.watched })
      if (targetId !== null) setPlan(await api.rewatchOrder(targetId))
    } catch (e) {
      setError(e)
    }
  }
  const percent = plan && plan.totalCount > 0 ? (plan.watchedCount / plan.totalCount) * 100 : 100
  return (
    <div className="space-y-6">
      <Card>
        <label htmlFor="target" className={labelClass}>I want to be ready for</label>
        <select
          id="target"
          value={targetId ?? ''}
          onChange={(e) => setTargetId(Number(e.target.value))}
          className={inputClass}
        >
          {movies.map((m) => (
            <option key={m.id} value={m.id} className="bg-black">
              {m.title} ({m.releaseYear})
            </option>
          ))}
        </select>
      </Card>
      <ErrorBox error={error} />
      {plan && (
        <Card>
          <div className="flex flex-wrap items-end justify-between gap-2">
            <h2 className="text-lg font-bold text-white sm:text-xl">Rewatch plan for {plan.target.title}</h2>
            <p className="text-sm font-semibold text-amber-300">
              {plan.unwatchedRuntimeMinutes > 0
                ? `${formatRuntime(plan.unwatchedRuntimeMinutes)} left`
                : 'All caught up'}
            </p>
          </div>
          <div className="mt-4">
            <div
              role="progressbar"
              aria-valuemin={0}
              aria-valuemax={plan.totalCount}
              aria-valuenow={plan.watchedCount}
              className="h-3 overflow-hidden rounded-full bg-emerald-950/80"
            >
              <div
                className="h-full rounded-full bg-linear-to-r from-emerald-500 to-amber-400 transition-all duration-500"
                style={{ width: `${percent}%` }}
              />
            </div>
            <p className="mt-2 text-sm text-emerald-200/80">
              {plan.watchedCount} of {plan.totalCount} watched
            </p>
          </div>
          {plan.movies.length === 0 ? (
            <p className="mt-6 text-emerald-100">
              Nothing to rewatch. {plan.target.title} has no prerequisites, so you are ready.
            </p>
          ) : (
            <ol className="mt-6 space-y-2">
              {plan.movies.map((movie, index) => (
                <li
                  key={movie.id}
                  className={`flex items-center gap-3 rounded-xl border px-3 py-3 transition sm:gap-4 sm:px-4 ${
                    movie.watched
                      ? 'border-emerald-900/40 bg-emerald-950/30'
                      : 'border-emerald-700/50 bg-black/20'
                  }`}
                >
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-900 text-xs font-bold text-amber-300 sm:h-8 sm:w-8 sm:text-sm">
                    {index + 1}
                  </span>
                  <Poster
                    title={movie.title}
                    className={`h-24 w-16 sm:h-36 sm:w-24 ${movie.watched ? 'opacity-50 grayscale' : ''}`}
                  />
                  <div className="min-w-0 flex-1">
                    <p
                      className={`text-base font-bold sm:text-xl ${
                        movie.watched ? 'text-emerald-200/60' : 'text-white'
                      }`}
                    >
                      {movie.title}
                    </p>
                    <p className="mt-1 text-sm text-emerald-200/70 sm:text-base">
                      {movie.releaseYear} {'\u00b7'} {formatRuntime(movie.runtimeMinutes)}
                    </p>
                  </div>
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={movie.watched}
                      onChange={() => toggleWatched(movie)}
                      aria-label={`Mark ${movie.title} as watched`}
                      className="h-5 w-5 accent-amber-400"
                    />
                    <span className="hidden sm:inline">Watched</span>
                  </label>
                </li>
              ))}
              <li className="flex items-center gap-3 rounded-xl border border-amber-400/50 bg-amber-400/10 px-3 py-3 sm:gap-4 sm:px-4">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-amber-400 text-xs font-bold text-black sm:h-8 sm:w-8 sm:text-sm">
                  {'\u2605'}
                </span>
                <Poster title={plan.target.title} className="h-16 w-11 ring-2 ring-amber-400 sm:h-20 sm:w-14" />
                <p className="text-base font-bold text-amber-100 sm:text-xl">Then watch {plan.target.title}</p>
              </li>
            </ol>
          )}
        </Card>
      )}
    </div>
  )
}
