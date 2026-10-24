import Link from 'next/link';

export default function NotFound() {
  return (
    <section className="mx-auto flex min-h-[60vh] max-w-xl flex-col items-center justify-center gap-6 px-[var(--gutter)] text-center">
      <p className="text-display text-6xl text-brass-300">Introuvable</p>
      <h1 className="text-xl">Cette pièce n’est plus en vitrine.</h1>
      <p className="text-zinc-400">Elle a peut-être été vendue, ou le lien est incomplet. La collection continue juste à côté.</p>
      <Link href="/catalogue" className="bg-ivory px-7 py-3.5 text-xs font-medium uppercase tracking-label text-ink-950 hover:bg-brass-300">
        Voir la collection
      </Link>
    </section>
  );
}
