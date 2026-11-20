const images = import.meta.glob<string>('./assets/posters/*.{jpg,jpeg,png,webp}', {
  eager: true,
  query: '?url',
  import: 'default',
})
export function slugify(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}
export function posterFor(title: string): string | undefined {
  const slug = slugify(title)
  const key = Object.keys(images).find((path) => path.split('/').pop()?.split('.')[0] === slug)
  return key ? images[key] : undefined
}
