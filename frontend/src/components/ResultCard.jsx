const VERDICTS = {
  fraud: {
    title: 'Likely Fraud',
    text: 'This message shows strong signs of a scam. Do not click links, call back, or share any details.',
    icon: '⛔',
  },
  suspicious: {
    title: 'Suspicious',
    text: 'Some warning signs found. Verify with the official source before acting.',
    icon: '⚠️',
  },
  safe: {
    title: 'Looks Safe',
    text: 'No common fraud patterns detected. Still, stay cautious with unknown senders.',
    icon: '✅',
  },
}

const TIPS = [
  'Banks never ask for OTP, PIN, CVV or passwords over SMS or calls.',
  'Check links carefully — official sites don’t use bit.ly or random domains.',
  'Call your bank using the number on the back of your card, not one in the message.',
  'Report fraud at cybercrime.gov.in or call 1930 (India).',
]

function Gauge({ score, verdict }) {
  const r = 52
  const c = 2 * Math.PI * r
  const offset = c - (score / 100) * c
  return (
    <div className={`gauge gauge-${verdict}`}>
      <svg viewBox="0 0 120 120" width="130" height="130">
        <circle cx="60" cy="60" r={r} className="gauge-track" />
        <circle
          cx="60" cy="60" r={r}
          className="gauge-bar"
          strokeDasharray={c}
          strokeDashoffset={offset}
          transform="rotate(-90 60 60)"
        />
      </svg>
      <div className="gauge-label">
        <strong>{score}</strong>
        <span>risk score</span>
      </div>
    </div>
  )
}

export default function ResultCard({ result, loading }) {
  if (loading) {
    return (
      <div className="card result empty">
        <div className="big-spinner" />
        <p>Scanning message for fraud patterns…</p>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="card result empty">
        <div className="empty-icon">🛡️</div>
        <h3>No message checked yet</h3>
        <p>Paste a message on the left and click <b>Check message</b> to see the analysis here.</p>
      </div>
    )
  }

  const v = VERDICTS[result.verdict]

  return (
    <div className={`card result result-${result.verdict}`}>
      <div className="verdict">
        <Gauge score={result.score} verdict={result.verdict} />
        <div>
          <div className={`badge badge-${result.verdict}`}>{v.icon} {v.title}</div>
          <p className="verdict-text">{v.text}</p>
          {result.sender && <p className="muted">Sender: <b>{result.sender}</b></p>}
        </div>
      </div>

      <h4>Red flags found ({result.flags.length})</h4>
      {result.flags.length ? (
        <ul className="flags">
          {result.flags.map((f, i) => (
            <li key={f.id + i}>
              <span>{f.label}</span>
              <span className="weight">+{f.weight}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">None detected.</p>
      )}

      {(result.numbers.length > 0 || result.links.length > 0) && (
        <>
          <h4>Extracted from message</h4>
          <div className="extracted">
            {result.numbers.map((n) => <span key={n} className="tag">📞 {n}</span>)}
            {result.links.map((l) => <span key={l} className="tag tag-link">🔗 {l}</span>)}
          </div>
        </>
      )}

      {result.verdict !== 'safe' && (
        <>
          <h4>What you should do</h4>
          <ul className="tips">
            {TIPS.map((t) => <li key={t}>{t}</li>)}
          </ul>
        </>
      )}
    </div>
  )
}
