export type Movie = {
  id: number
  title: string
  releaseYear: number
  runtimeMinutes: number
  watched: boolean
  description: string | null
  prerequisiteIds: number[]
}
export type MovieInput = {
  title: string
  releaseYear: number
  runtimeMinutes: number
  prerequisiteIds: number[]
}
export type MoviePatch = Partial<MovieInput & { watched: boolean }>
export type RewatchPlan = {
  target: Movie
  movies: Movie[]
  totalCount: number
  watchedCount: number
  unwatchedRuntimeMinutes: number
}
export type Cinema = {
  id: number
  name: string
  bundleSizes: number[]
}
export type BookingQuote = {
  cinemaId: number
  groupSize: number
  possible: boolean
  totalBundles: number | null
  bundles: { size: number; count: number }[]
  message: string
}
export class ApiError extends Error {
  status: number
  code: string
  details?: Record<string, unknown>
  constructor(status: number, code: string, message: string, details?: Record<string, unknown>) {
    super(message)
    this.status = status
    this.code = code
    this.details = details
  }
}
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`/api${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', 'Cannot reach the server. Is the backend running?')
  }
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    const error = body?.error
    throw new ApiError(
      response.status,
      error?.code ?? 'UNKNOWN_ERROR',
      error?.message ?? `Request failed with status ${response.status}.`,
      error?.details,
    )
  }
  return body as T
}
export const api = {
  listMovies: () => request<Movie[]>('/movies'),
  createMovie: (input: MovieInput) =>
    request<Movie>('/movies', { method: 'POST', body: JSON.stringify(input) }),
  updateMovie: (id: number, patch: MoviePatch) =>
    request<Movie>(`/movies/${id}`, { method: 'PATCH', body: JSON.stringify(patch) }),
  rewatchOrder: (id: number) => request<RewatchPlan>(`/movies/${id}/rewatch-order`),
  listCinemas: () => request<Cinema[]>('/cinemas'),
  createCinema: (name: string, bundleSizes: number[]) =>
    request<Cinema>('/cinemas', { method: 'POST', body: JSON.stringify({ name, bundleSizes }) }),
  bookingQuote: (id: number, groupSize: number) =>
    request<BookingQuote>(`/cinemas/${id}/booking?groupSize=${groupSize}`),
}
export function formatRuntime(minutes: number): string {
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  if (hours === 0) return `${rest}m`
  return rest === 0 ? `${hours}h` : `${hours}h ${rest}m`
}
