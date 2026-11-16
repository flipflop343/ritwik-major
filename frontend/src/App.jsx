import { useEffect, useState } from 'react'
import Header from './components/Header.jsx'
import MessageChecker from './components/MessageChecker.jsx'
import ResultCard from './components/ResultCard.jsx'
import HistoryList from './components/HistoryList.jsx'
import Features from './components/Features.jsx'
import { analyzeMessage } from './utils/analyzer.js'

const HISTORY_KEY = 'fraudshield-history'

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []
  } catch {
    return []
  }
}

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState(loadHistory)

  useEffect(() => {
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history))
    } catch {
      /* storage unavailable */
    }
  }, [history])

  const handleCheck = async (input) => {
    setLoading(true)
    setResult(null)
    const res = await analyzeMessage(input)
    setResult(res)
    setHistory((h) => [res, ...h].slice(0, 10))
    setLoading(false)
  }

  return (
    <div className="app">
      <Header />
      <main className="container">
        <section className="hero">
          <h1>
            Is this message a <span className="accent">scam?</span>
          </h1>
          <p>
            Paste an SMS, WhatsApp or email message and the sender's number. We'll check it for
            common fraud patterns like fake KYC alerts, OTP requests, and credit-card scams.
          </p>
        </section>

        <div className="grid">
          <MessageChecker onCheck={handleCheck} loading={loading} />
          <ResultCard result={result} loading={loading} />
        </div>

        <HistoryList
          history={history}
          onSelect={setResult}
          onClear={() => setHistory([])}
        />
        <Features />
      </main>
      <footer className="footer">
        FraudShield · Major Project · Results are indicative — never share OTPs, PINs or card details.
      </footer>
    </div>
  )
}
