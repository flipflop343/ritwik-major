const LABEL = { fraud: 'Fraud', suspicious: 'Suspicious', safe: 'Safe' }

export default function HistoryList({ history, onSelect, onClear }) {
  return (
    <section id="history" className="card section">
      <div className="card-title">
        <h2>Recent checks</h2>
        {history.length > 0 && (
          <button type="button" className="btn-ghost" onClick={onClear}>Clear history</button>
        )}
      </div>
      {history.length === 0 ? (
        <p className="muted">Your last 10 checks will appear here (stored only in this browser).</p>
      ) : (
        <ul className="history">
          {history.map((h) => (
            <li key={h.id}>
              <button type="button" onClick={() => { onSelect(h); window.scrollTo({ top: 0, behavior: 'smooth' }) }}>
                <span className={`dot dot-${h.verdict}`} />
                <span className="history-msg">{h.message}</span>
                <span className={`badge badge-sm badge-${h.verdict}`}>{LABEL[h.verdict]} · {h.score}</span>
                <span className="muted history-time">
                  {new Date(h.checkedAt).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
