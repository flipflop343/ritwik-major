const FEATURES = [
  { icon: '🔍', title: 'Message pattern analysis', text: 'Detects KYC, OTP, prize and card-fraud language.', status: 'live' },
  { icon: '🌐', title: 'Internet search', text: 'Search the web for complaints about the number or link.', status: 'soon' },
  { icon: '📇', title: 'Number reputation lookup', text: 'Check the sender against a crowd-sourced fraud database.', status: 'soon' },
  { icon: '🤖', title: 'ML fraud model', text: 'Trained classifier for SMS and credit-card fraud.', status: 'soon' },
  { icon: '🔗', title: 'URL safety scan', text: 'Check links against phishing and malware lists.', status: 'soon' },
  { icon: '📣', title: 'Report a number', text: 'Let users report fraud numbers to protect others.', status: 'soon' },
]

export default function Features() {
  return (
    <section id="features" className="section">
      <h2 className="section-title">Features</h2>
      <div className="features">
        {FEATURES.map((f) => (
          <div key={f.title} className="feature">
            <div className="feature-icon">{f.icon}</div>
            <div>
              <div className="feature-head">
                <h3>{f.title}</h3>
                <span className={`pill pill-${f.status}`}>{f.status === 'live' ? 'Live' : 'Coming soon'}</span>
              </div>
              <p>{f.text}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
