type Props = {
  onStart: (view: 'movies' | 'rewatch' | 'booking') => void
}
export default function Landing({ onStart }: Props) {
  return (
    <section className="flex min-h-screen flex-col items-center justify-end px-6 pb-16 text-center sm:pb-24">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-amber-400/90 sm:text-sm sm:tracking-[0.4em]">
        Before the premiere
      </p>
      <h1 className="mt-3 text-4xl font-black tracking-tight text-white drop-shadow-lg sm:text-7xl">
        Doomsday Ready
      </h1>
      <p className="mt-4 max-w-xl text-base text-emerald-100/85 sm:text-lg">
        Plan your MCU rewatch in the right order, then book an opening night watch party for your
        whole group.
      </p>
      <div className="mt-8 flex w-full flex-col justify-center gap-3 sm:w-auto sm:flex-row">
        <button
          onClick={() => onStart('rewatch')}
          className="rounded-xl bg-emerald-600 px-6 py-3 text-base font-semibold text-white shadow-lg transition hover:bg-emerald-500 sm:text-lg"
        >
          Plan my rewatch
        </button>
        <button
          onClick={() => onStart('booking')}
          className="rounded-xl border border-amber-400/70 bg-black/40 px-6 py-3 text-base font-semibold text-amber-200 backdrop-blur-sm transition hover:bg-amber-400/10 sm:text-lg"
        >
          Book a watch party
        </button>
      </div>
      <button
        onClick={() => onStart('movies')}
        className="mt-5 text-sm text-emerald-200/80 underline-offset-4 hover:underline"
      >
        Manage movies
      </button>
    </section>
  )
}
