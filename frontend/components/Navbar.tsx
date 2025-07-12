import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="flex items-center">
        <Link href="/" className="text-[#ff1801] text-2xl font-bold hover:text-[#cc1401] transition-colors">
          🏎️ RuleBox F1
        </Link>
      </div>
      <div className="flex gap-2">
        <Link href="/" className="navbar-link">
          Home
        </Link>
        <Link href="/query" className="navbar-link">
          Search
        </Link>
        <Link href="/ai-chat" className="navbar-link">
          AI Chat
        </Link>
        <Link href="/auth/login" className="navbar-link">
          Login
        </Link>
      </div>
    </nav>
  );
}
