import { useEffect, useRef, useState } from 'react'
import { landingBackground, pagesBackground } from './backgrounds'
import BookingView from './views/BookingView'
import Landing from './views/Landing'
import MoviesView from './views/MoviesView'
import RewatchView from './views/RewatchView'
type View = 'landing' | 'movies' | 'rewatch' | 'booking'
const views: View[] = ['landing', 'movies', 'rewatch', 'booking']
const tabs: { id: Exclude<View, 'landing'>; label: string }[] = [
  { id: 'movies', label: 'Movies' },
  { id: 'rewatch', label: 'Rewatch Plan' },
  { id: 'booking', label: 'Booking' },
]
function viewFromHash(): View {
  const hash = window.location.hash.replace('#', '') as View
  return views.includes(hash) ? hash : 'landing'
}
function App() {
  const [view, setView] = useState<View>(viewFromHash)
  const steps = useRef(0)
  useEffect(() => {
    const onPopState = () => {
      steps.current = Math.max(0, steps.current - 1)
      setView(viewFromHash())
    }
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])
  function go(next: View) {
    if (next === view) return
    window.history.pushState(null, '', next === 'landing' ? window.location.pathname : `#${next}`)
    steps.current += 1
    setView(next)
    window.scrollTo(0, 0)
  }
  function goBack() {
    if (steps.current > 0) {
      window.history.back()
    } else {
      go('landing')
    }
  }
  const background = view === 'landing' ? landingBackground : pagesBackground
  return (
    <div className="relative min-h-screen text-emerald-50">
      <div
        aria-hidden
        className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,#0f3d2e_0%,#04120d_65%)]"
      />
      {background && (
        <div
          aria-hidden
          className="fixed inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${background})` }}
        />
      )}
      <div
        aria-hidden
        className={`fixed inset-0 ${
          view === 'landing' ? 'bg-linear-to-b from-black/30 via-black/20 to-black/85' : 'bg-black/45'
        }`}
      />
      <div className="relative">
        {view === 'landing' ? (
          <Landing onStart={go} />
        ) : (
          <>
            <div className="px-4 pt-4">
              <button
                onClick={goBack}
                aria-label="Go back"
                className="flex items-center gap-1.5 rounded-lg border border-emerald-700/60 bg-black/30 px-3 py-1.5 text-sm text-emerald-100 backdrop-blur-[3px] transition hover:bg-emerald-900/50"
              >
                <span aria-hidden>{'\u2190'}</span>
                Back
              </button>
            </div>
            <header className="mx-auto flex max-w-5xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:py-5">
              <button
                onClick={() => go('landing')}
                className="self-start text-lg font-black tracking-[0.2em] text-amber-400 [text-shadow:0_2px_6px_rgb(0_0_0/0.9)] sm:self-auto sm:text-xl sm:tracking-[0.25em]"
              >
                DOOMSDAY READY
              </button>
              <nav className="flex w-full gap-1 rounded-xl border border-emerald-700/40 bg-black/30 p-1 backdrop-blur-[3px] sm:w-auto">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => go(tab.id)}
                    aria-current={view === tab.id ? 'page' : undefined}
                    className={`flex-1 rounded-lg px-2 py-2 text-xs font-semibold transition sm:flex-none sm:px-4 sm:text-sm ${
                      view === tab.id
                        ? 'bg-emerald-600 text-white'
                        : 'text-emerald-200 hover:bg-emerald-900/60'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </nav>
            </header>
            <main className="mx-auto max-w-5xl px-4 pb-16">
              {view === 'movies' && <MoviesView />}
              {view === 'rewatch' && <RewatchView />}
              {view === 'booking' && <BookingView />}
            </main>
          </>
        )}
      </div>
    </div>
  )
}
export default App
