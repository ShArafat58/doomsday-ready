const images = import.meta.glob<string>('./assets/backgrounds/*.{jpg,jpeg,png,webp}', {
  eager: true,
  query: '?url',
  import: 'default',
})
function find(name: string): string | undefined {
  const key = Object.keys(images).find((path) => path.includes(name))
  return key ? images[key] : undefined
}
export const landingBackground = find('doom-landing')
export const pagesBackground = find('doom-pages')
