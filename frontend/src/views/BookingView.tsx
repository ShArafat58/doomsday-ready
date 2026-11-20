import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api'
import type { BookingQuote, Cinema } from '../api'
import { inputClass, labelClass, primaryButton, secondaryButton } from '../styles'
import { Card, ErrorBox } from '../ui'
export default function BookingView() {
  const [cinemas, setCinemas] = useState<Cinema[]>([])
  const [cinemaId, setCinemaId] = useState<number | null>(null)
  const [groupSize, setGroupSize] = useState('')
  const [quote, setQuote] = useState<BookingQuote | null>(null)
  const [error, setError] = useState<unknown>(null)
  const [newName, setNewName] = useState('')
  const [newSizes, setNewSizes] = useState('')
  const [createError, setCreateError] = useState<unknown>(null)
  useEffect(() => {
    api
      .listCinemas()
      .then((list) => {
        setCinemas(list)
        if (list.length > 0) setCinemaId(list[0].id)
      })
      .catch(setError)
  }, [])
  const selected = cinemas.find((c) => c.id === cinemaId)
  function chooseCinema(id: number) {
    setCinemaId(id)
    setQuote(null)
    setError(null)
  }
  async function handleQuote(event: FormEvent) {
    event.preventDefault()
    if (cinemaId === null) return
    setError(null)
    setQuote(null)
    try {
      setQuote(await api.bookingQuote(cinemaId, Number(groupSize)))
    } catch (e) {
      setError(e)
    }
  }
  async function handleCreate(event: FormEvent) {
    event.preventDefault()
    setCreateError(null)
    const sizes = newSizes.split(/[\s,]+/).filter(Boolean).map(Number)
    if (sizes.length === 0 || sizes.some((n) => !Number.isInteger(n))) {
      setCreateError(new Error('Enter bundle sizes as whole numbers, for example: 2, 5'))
      return
    }
    try {
      const created = await api.createCinema(newName, sizes)
      setCinemas((current) => [...current, created].sort((a, b) => a.name.localeCompare(b.name)))
      chooseCinema(created.id)
      setNewName('')
      setNewSizes('')
    } catch (e) {
      setCreateError(e)
    }
  }
  return (
    <div className="space-y-6">
      <Card>
        <h2 className="text-xl font-bold text-white">Opening night booking</h2>
        <form onSubmit={handleQuote} className="mt-4 space-y-4">
          <div className="grid gap-4 sm:grid-cols-[1fr_180px]">
            <div>
              <label htmlFor="cinema" className={labelClass}>Cinema</label>
              <select
                id="cinema"
                value={cinemaId ?? ''}
                onChange={(e) => chooseCinema(Number(e.target.value))}
                className={inputClass}
              >
                {cinemas.map((c) => (
                  <option key={c.id} value={c.id} className="bg-black">
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="group" className={labelClass}>Group size</label>
              <input
                id="group"
                type="number"
                required
                min={1}
                max={10000}
                value={groupSize}
                onChange={(e) => setGroupSize(e.target.value)}
                placeholder="44"
                className={inputClass}
              />
            </div>
          </div>
          {selected && (
            <div className="flex flex-wrap items-center gap-2 text-sm text-emerald-200/80">
              <span>Sold in bundles of</span>
              {selected.bundleSizes.map((size) => (
                <span key={size} className="rounded-full border border-emerald-700 px-2.5 py-0.5 text-xs">
                  {size} seats
                </span>
              ))}
            </div>
          )}
          <button type="submit" disabled={cinemaId === null} className={primaryButton}>
            Get quote
          </button>
        </form>
      </Card>
      <ErrorBox error={error} />
      {quote &&
        (quote.possible ? (
          <Card className="border-amber-400/50">
            <p className="text-sm uppercase tracking-wider text-amber-300">Best option</p>
            <p className="mt-1 text-3xl font-black text-white">
              {quote.totalBundles} {quote.totalBundles === 1 ? 'bundle' : 'bundles'}
            </p>
            <p className="text-sm text-emerald-200/70">
              Exactly {quote.groupSize} seats, no empty seat to pay for.
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              {quote.bundles.map((line) => (
                <div key={line.size} className="rounded-xl border border-emerald-700 bg-emerald-950/50 px-4 py-3">
                  <p className="text-2xl font-bold text-amber-300">{line.count} {'\u00d7'}</p>
                  <p className="text-sm text-emerald-100">bundle of {line.size}</p>
                </div>
              ))}
            </div>
          </Card>
        ) : (
          <Card className="border-red-500/50">
            <p className="text-3xl font-black text-red-300">Not possible</p>
            <p className="mt-1 text-sm text-red-100/80">{quote.message}</p>
          </Card>
        ))}
      <Card>
        <h3 className="font-semibold text-white">Add a cinema</h3><p className="mt-1 text-xs text-emerald-200/70">Use 1 to 10 different bundle sizes, each from 1 to 500 seats, separated by commas. Example: 2, 5</p>
        <form onSubmit={handleCreate} className="mt-3 grid gap-3 sm:grid-cols-[1fr_200px_auto] sm:items-end">
          <div>
            <label htmlFor="cinema-name" className={labelClass}>Name</label>
            <input
              id="cinema-name"
              required
              maxLength={200}
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Midnight Screens"
              className={inputClass}
            />
          </div>
          <div>
            <label htmlFor="cinema-sizes" className={labelClass}>Bundle sizes</label>
            <input
              id="cinema-sizes"
              required
              value={newSizes}
              onChange={(e) => setNewSizes(e.target.value)}
              placeholder="2, 5"
              className={inputClass}
            />
          </div>
          <button type="submit" className={secondaryButton}>Add cinema</button>
        </form>
        <div className="mt-3">
          <ErrorBox error={createError} />
        </div>
      </Card>
    </div>
  )
}
