import Link from 'next/link';

export default function Header() {
  return (
    <header className="border-b border-border-subtle bg-bg-primary/80 backdrop-blur-sm sticky top-0 z-40">
      <div className="max-w-content mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="text-accent-gold font-semibold text-lg">
          Islamic Hive Mind
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link href="/quran" className="text-text-primary hover:text-accent-gold transition-colors">
            Quran
          </Link>
          <span className="text-text-secondary cursor-default" title="Coming soon — we're crafting this section with care">
            Stories
          </span>
          <span className="text-text-secondary cursor-default" title="Coming soon — we're crafting this section with care">
            Discoveries
          </span>
          <Link href="/ask" className="text-accent-gold hover:text-accent-gold-dim transition-colors">
            Ask The Scholar
          </Link>
        </nav>
      </div>
    </header>
  );
}
