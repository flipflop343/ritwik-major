import { useState } from 'react'
import { SAMPLE_MESSAGES } from '../utils/analyzer.js'

const MAX_LEN = 2000

export default function MessageChecker({ onCheck, loading }) {
  const [message, setMessage] = useState('')
  const [sender, setSender] = useState('')
  const [error, setError] = useState('')

  const submit = (e) => {
    e.preventDefault()
    if (message.trim().length < 5) {
      setError('Please paste the message you want to check.')
      return
    }
    if (sender && !/^[+\d\s()-]{6,20}$/.test(sender.trim())) {
      setError('Sender number looks invalid. Use digits, spaces, + or -.')
      return
    }
    setError('')
    onCheck({ message: message.trim(), sender: sender.trim() })
  }

  const paste = async () => {
    try {
      const text = await navigator.clipboard.readText()
      if (text) setMessage(text.slice(0, MAX_LEN))
    } catch {
      setError('Clipboard access was blocked — paste manually with Ctrl+V.')
    }
  }

  const loadSample = (s) => {
    setMessage(s.message)
    setSender(s.sender)
    setError('')
  }

  const clear = () => {
    setMessage('')
    setSender('')
    setError('')
  }

  return (
    <form id="checker" className="card" onSubmit={submit}>
      <div className="card-title">
        <h2>Check a message</h2>
        <button type="button" className="btn-ghost" onClick={paste}>
          Paste from clipboard
        </button>
      </div>

      <label className="label" htmlFor="sender">Sender number (optional)</label>
      <input
        id="sender"
        className="input"
        type="tel"
        placeholder="e.g. +91 98765 43210"
        value={sender}
        onChange={(e) => setSender(e.target.value)}
      />

      <label className="label" htmlFor="message">Message</label>
      <textarea
        id="message"
        className="input textarea"
        placeholder="Paste the suspicious SMS, WhatsApp or email text here…"
        value={message}
        maxLength={MAX_LEN}
        onChange={(e) => setMessage(e.target.value)}
      />
      <div className="counter">{message.length}/{MAX_LEN}</div>

      {error && <div className="error">{error}</div>}

      <div className="actions">
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? <span className="spinner" /> : null}
          {loading ? 'Analyzing…' : 'Check message'}
        </button>
        <button type="button" className="btn-secondary" onClick={clear} disabled={loading}>
          Clear
        </button>
      </div>

      <div className="samples">
        <span>Try a sample:</span>
        {SAMPLE_MESSAGES.map((s) => (
          <button key={s.title} type="button" className="chip" onClick={() => loadSample(s)}>
            {s.title}
          </button>
        ))}
      </div>
    </form>
  )
}
