export function DocumentViewer({ url, mime }: { url: string; mime?: string }) {
  if (!url) return <div className="text-slate-400">No preview URL</div>
  if (mime?.includes('pdf')) {
    return <iframe title="document" src={url} className="w-full h-[520px] rounded-lg border border-border" />
  }
  if (mime?.startsWith('image/')) {
    return <img src={url} alt="document" className="max-h-[520px] rounded-lg border border-border" />
  }
  return (
    <a href={url} target="_blank" rel="noreferrer" className="text-primary underline">
      Open file
    </a>
  )
}
