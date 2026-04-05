import Link from 'next/link';

interface ButtonProps {
  children: React.ReactNode;
  href?: string;
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
  className?: string;
}

export default function Button({ children, href, variant = 'primary', onClick, className = '' }: ButtonProps) {
  const base = 'inline-flex items-center justify-center px-6 py-3 rounded-lg font-medium text-sm transition-colors';
  const styles = variant === 'primary'
    ? 'bg-accent-gold text-bg-primary hover:bg-accent-gold-dim'
    : 'border border-accent-gold/40 text-accent-gold hover:bg-accent-gold/10';

  if (href) {
    return <Link href={href} className={`${base} ${styles} ${className}`}>{children}</Link>;
  }
  return <button onClick={onClick} className={`${base} ${styles} ${className}`}>{children}</button>;
}
