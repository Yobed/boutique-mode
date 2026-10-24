/** Splits a sentence into word spans for scroll choreography; screen readers get the plain text. */
export default function Words({ text, className = '' }: { text: string; className?: string }) {
  return (
    <>
      <span className="sr-only">{text}</span>
      <span aria-hidden className={className}>
        {text.split(' ').map((w, i) => (
          <span key={i} data-word className="inline-block">
            {w}&nbsp;
          </span>
        ))}
      </span>
    </>
  );
}
