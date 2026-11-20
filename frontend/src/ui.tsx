import type { ReactNode } from 'react'
import { ApiError } from './api'
export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={`rounded-2xl border border-emerald-700/40 bg-black/25 p-4 shadow-xl backdrop-blur-[3px] [text-shadow:0_1px_3px_rgb(0_0_0/0.8)] sm:p-5 ${className}`}
    >
      {children}
    </div>
  )
}
export function ErrorBox({ error }: { error: unknown }) {
  if (!error) return null
  const message = error instanceof Error ? error.message : String(error)
  const cycle =
    error instanceof ApiError && error.code === 'CIRCULAR_DEPENDENCY'
      ? (error.details?.cycle as string[] | undefined)
      : undefined
  return (
    <div role="alert" className="rounded-xl border border-red-500/50 bg-red-950/70 p-4 text-sm text-red-100 backdrop-blur-sm">
      {cycle ? (
        <>
          <p className="font-semibold">Circular dependency</p>
          <p className="mt-1 text-red-200">This change would make a movie depend on itself:</p>
          <p className="mt-2 font-medium">{cycle.join(' \u2192 ')}</p>
        </>
      ) : (
        <p>{message}</p>
      )}
    </div>
  )
}
