export default function Loading() {
  return (
    <div role="status" aria-label="Chargement de la pièce" className="mx-auto grid max-w-[1440px] gap-10 px-[var(--gutter)] pt-16 lg:grid-cols-[1.15fr_1fr] lg:gap-16">
      <div className="skeleton aspect-[3/4]" />
      <div className="space-y-5 pt-4">
        <div className="skeleton h-4 w-24" />
        <div className="skeleton h-12 w-4/5" />
        <div className="skeleton h-6 w-32" />
        <div className="skeleton h-24 w-full" />
        <div className="skeleton h-14 w-full" />
      </div>
    </div>
  );
}
