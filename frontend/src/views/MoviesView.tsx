import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { api, formatRuntime } from '../api'
import type { Movie } from '../api'
import Poster from '../Poster'
import { inputClass, labelClass, primaryButton, secondaryButton } from '../styles'
import { Card, ErrorBox } from '../ui'
const byYearThenTitle = (a: Movie, b: Movie) =>
  a.releaseYear - b.releaseYear || a.title.localeCompare(b.title)
type PickerProps = {
  movies: Movie[]
  selected: number[]
  onChange: (ids: number[]) => void
  excludeId?: number
}
function PrerequisitePicker({ movies, selected, onChange, excludeId }: PickerProps) {
  const options = movies.filter((m) => m.id !== excludeId)
  if (options.length === 0) {
    return <p className="text-sm text-emerald-200/60">No other movies yet.</p>
  }
  const toggle = (id: number) =>
    onChange(selected.includes(id) ? selected.filter((x) => x !== id) : [...selected, id])
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((m) => {
        const active = selected.includes(m.id)
        return (
          <button
            key={m.id}
            type="button"
            aria-pressed={active}
            onClick={() => toggle(m.id)}
            className={`rounded-full border px-3 py-1 text-xs transition ${
              active
                ? 'border-amber-400 bg-amber-400/20 text-amber-100'
                : 'border-emerald-800 text-emerald-200/80 hover:border-emerald-500'
            }`}
          >
            {m.title}
          </button>
        )
      })}
    </div>
  )
}
export default function MoviesView() {
  const [movies, setMovies] = useState<Movie[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)
  const [title, setTitle] = useState('')
  const [releaseYear, setReleaseYear] = useState('')
  const [runtime, setRuntime] = useState('')
  const [newPrerequisites, setNewPrerequisites] = useState<number[]>([])
  const [formError, setFormError] = useState<unknown>(null)
  const [saving, setSaving] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [draft, setDraft] = useState<number[]>([])
  const [editError, setEditError] = useState<unknown>(null)
  const titles = useMemo(() => new Map(movies.map((m) => [m.id, m.title])), [movies])
  useEffect(() => {
    api
      .listMovies()
      .then((list) => setMovies(list.sort(byYearThenTitle)))
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])
  function replaceMovie(updated: Movie) {
    setMovies((current) => current.map((m) => (m.id === updated.id ? updated : m)))
  }
  async function handleCreate(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setFormError(null)
    try {
      const created = await api.createMovie({
        title,
        releaseYear: Number(releaseYear),
        runtimeMinutes: Number(runtime),
        prerequisiteIds: newPrerequisites,
      })
      setMovies((current) => [...current, created].sort(byYearThenTitle))
      setTitle('')
      setReleaseYear('')
      setRuntime('')
      setNewPrerequisites([])
    } catch (e) {
      setFormError(e)
    } finally {
      setSaving(false)
    }
  }
  async function toggleWatched(movie: Movie) {
    setError(null)
    try {
      replaceMovie(await api.updateMovie(movie.id, { watched: !movie.watched }))
    } catch (e) {
      setError(e)
    }
  }
  function startEdit(movie: Movie) {
    setEditingId(movie.id)
    setDraft(movie.prerequisiteIds)
    setEditError(null)
  }
  async function saveEdit(movie: Movie) {
    setEditError(null)
    try {
      replaceMovie(await api.updateMovie(movie.id, { prerequisiteIds: draft }))
      setEditingId(null)
    } catch (e) {
      setEditError(e)
    }
  }
  return (
    <div className="space-y-6">
      <Card>
        <h2 className="text-xl font-bold text-white">Add a movie</h2>
        <form onSubmit={handleCreate} className="mt-4 space-y-4">
          <div className="grid gap-4 sm:grid-cols-[1fr_130px_150px]">
            <div>
              <label htmlFor="title" className={labelClass}>Title</label>
              <input
                id="title"
                required
                maxLength={200}
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Thor: Love and Thunder"
                className={inputClass}
              />
            </div>
            <div>
              <label htmlFor="year" className={labelClass}>Release year</label>
              <input
                id="year"
                type="number"
                required
                min={1900}
                max={2100}
                value={releaseYear}
                onChange={(e) => setReleaseYear(e.target.value)}
                placeholder="2022"
                className={inputClass}
              />
            </div>
            <div>
              <label htmlFor="runtime" className={labelClass}>Runtime (min)</label>
              <input
                id="runtime"
                type="number"
                required
                min={1}
                max={300}
                value={runtime}
                onChange={(e) => setRuntime(e.target.value)}
                placeholder="119"
                className={inputClass}
              />
            </div>
          </div>
          <div>
            <span className={labelClass}>Watch these first</span>
            <PrerequisitePicker movies={movies} selected={newPrerequisites} onChange={setNewPrerequisites} />
          </div>
          <ErrorBox error={formError} />
          <button type="submit" disabled={saving} className={primaryButton}>
            {saving ? 'Adding...' : 'Add movie'}
          </button>
        </form>
      </Card>
      <ErrorBox error={error} />
      <section>
        <h2 className="mb-3 text-xl font-bold text-white [text-shadow:0_2px_6px_rgb(0_0_0/0.9)]">
          Movies ({movies.length})
        </h2>
        {loading ? (
          <p className="text-emerald-200/70">Loading movies...</p>
        ) : movies.length === 0 ? (
          <Card>No movies yet. Add the first one above.</Card>
        ) : (
          <ul className="space-y-3">
            {movies.map((movie) => (
              <li key={movie.id}>
                <Card>
                  <div className="flex gap-4">
                    <Poster
                      title={movie.title}
                      className={`h-20 w-14 sm:h-28 sm:w-20 ${movie.watched ? 'opacity-50 grayscale' : ''}`}
                    />
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <h3 className="text-base font-semibold text-white sm:text-lg">{movie.title}</h3>
                          <p className="text-sm text-emerald-200/70">
                            {movie.releaseYear} {'\u00b7'} {formatRuntime(movie.runtimeMinutes)}
                          </p>
                        </div>
                        <div className="flex items-center gap-3">
                          <label className="flex items-center gap-2 text-sm">
                            <input
                              type="checkbox"
                              checked={movie.watched}
                              onChange={() => toggleWatched(movie)}
                              className="h-4 w-4 accent-amber-400"
                            />
                            Watched
                          </label>
                          {editingId !== movie.id && (
                            <button onClick={() => startEdit(movie)} className={secondaryButton}>
                              Edit prerequisites
                            </button>
                          )}
                        </div>
                      </div>
                      {editingId === movie.id ? (
                        <div className="mt-4 space-y-3 border-t border-emerald-900/60 pt-4">
                          <span className={labelClass}>Watch these first</span>
                          <PrerequisitePicker
                            movies={movies}
                            selected={draft}
                            onChange={setDraft}
                            excludeId={movie.id}
                          />
                          <ErrorBox error={editError} />
                          <div className="flex gap-2">
                            <button onClick={() => saveEdit(movie)} className={primaryButton}>Save</button>
                            <button onClick={() => setEditingId(null)} className={secondaryButton}>Cancel</button>
                          </div>
                        </div>
                      ) : (
                        <div className="mt-3 flex flex-wrap items-center gap-2">
                          <span className="text-xs text-emerald-200/60">Watch first:</span>
                          {movie.prerequisiteIds.length === 0 ? (
                            <span className="text-xs text-emerald-200/50">nothing</span>
                          ) : (
                            movie.prerequisiteIds.map((id) => (
                              <span
                                key={id}
                                className="rounded-full border border-emerald-800 px-2.5 py-0.5 text-xs text-emerald-200/80"
                              >
                                {titles.get(id)}
                              </span>
                            ))
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
