export default function LoadingDots() {
  return (
    <div className="flex gap-1 py-2">
      {[0, 1, 2].map((i) => (
        <div key={i} className="w-2 h-2 rounded-full bg-accent-gold animate-pulse" style={{ animationDelay: `${i * 200}ms` }} />
      ))}
    </div>
  );
}
