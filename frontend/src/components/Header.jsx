export default function Header() {
  return (
    <header className="header">
      <div className="container header-inner">
        <div className="brand">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
          <span>FraudShield</span>
        </div>
        <nav className="nav">
          <a href="#checker">Checker</a>
          <a href="#history">History</a>
          <a href="#features">Features</a>
        </nav>
      </div>
    </header>
  )
}
