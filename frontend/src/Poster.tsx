import { posterFor } from './posters'
export default function Poster({ title, className = '' }: { title: string; className?: string }) {
  const src = posterFor(title)
  if (!src) {
    const initials = title
      .split(/\s+/)
      .filter((word) => /^[A-Za-z0-9]/.test(word))
      .slice(0, 2)
      .map((word) => word[0].toUpperCase())
      .join('')
    return (
      <div
        aria-hidden
        className={`flex shrink-0 items-center justify-center rounded-md bg-emerald-950 text-sm font-bold text-emerald-300 ${className}`}
      >
        {initials}
      </div>
    )
  }
  return (
    <img
      src={src}
      alt={`${title} poster`}
      loading="lazy"
      className={`shrink-0 rounded-md object-cover shadow-lg ${className}`}
    />
  )
}
