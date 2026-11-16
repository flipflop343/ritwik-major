/**
 * TEMPORARY client-side analyzer.
 *
 * This is a rule-based placeholder so the UI works end-to-end before the
 * backend exists. Later, replace the body of `analyzeMessage` with a call to
 * your API (ML model, number reputation lookup, internet search, etc.) and
 * keep the same return shape so the UI doesn't need to change.
 */

const RULES = [
  { id: 'otp', label: 'Asks for OTP / PIN / CVV', weight: 30,
    pattern: /\b(otp|one[\s-]?time[\s-]?password|pin|cvv|cvc|mpin|upi\s?pin)\b/i },
  { id: 'kyc', label: 'KYC / account update threat', weight: 25,
    pattern: /\b(kyc|update (your )?(pan|aadhaar|account|details)|re-?verify|verification pending)\b/i },
  { id: 'blocked', label: 'Account blocked / suspended threat', weight: 25,
    pattern: /\b(blocked|suspended|deactivated|frozen|will be (closed|terminated)|disabled)\b/i },
  { id: 'urgency', label: 'Creates urgency', weight: 15,
    pattern: /\b(urgent|immediately|within \d+ ?(hours?|hrs?|minutes?|mins?)|today only|last chance|act now|expire[sd]?)\b/i },
  { id: 'prize', label: 'Lottery / prize / reward bait', weight: 25,
    pattern: /\b(congratulations|you (have )?won|lottery|lucky draw|prize|reward|cashback of|jackpot|gift card)\b/i },
  { id: 'card', label: 'Mentions credit/debit card', weight: 10,
    pattern: /\b(credit card|debit card|card (number|details)|atm card)\b/i },
  { id: 'money', label: 'Requests payment or transfer', weight: 15,
    pattern: /\b(pay|transfer|send money|processing fee|refund|deposit|rs\.?\s?\d+|₹\s?\d+|inr\s?\d+)\b/i },
  { id: 'link', label: 'Contains a link', weight: 10,
    pattern: /(https?:\/\/|www\.)\S+/i },
  { id: 'shortlink', label: 'Shortened / disguised link', weight: 20,
    pattern: /\b(bit\.ly|tinyurl|goo\.gl|t\.co|cutt\.ly|rb\.gy|is\.gd|shorturl)\b/i },
  { id: 'apk', label: 'Asks to install an app / APK', weight: 25,
    pattern: /\b(\.apk|anydesk|teamviewer|quicksupport|download (the )?app|install (this|the) app)\b/i },
  { id: 'job', label: 'Work-from-home / easy money offer', weight: 20,
    pattern: /\b(work from home|part[\s-]?time job|earn \S+ (per|a) day|daily income|like (youtube )?videos)\b/i },
  { id: 'click', label: 'Asks you to click / call back', weight: 10,
    pattern: /\b(click (here|the link|below)|call (us|now|immediately)|contact (immediately|now))\b/i },
]

const PHONE_RE = /(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){9,12}\d/g
const URL_RE = /(https?:\/\/[^\s]+|www\.[^\s]+)/gi

// Placeholder "known fraud" list — will come from the database later.
const REPORTED_NUMBERS = new Set(['9876543210', '8001234567', '7012345678'])

const normalizeNumber = (n) => n.replace(/\D/g, '').slice(-10)

function senderFlags(sender) {
  const flags = []
  if (!sender) return { flags, score: 0 }
  const digits = sender.replace(/\D/g, '')
  let score = 0

  if (digits && REPORTED_NUMBERS.has(normalizeNumber(sender))) {
    flags.push({ id: 'reported', label: 'Sender number reported as fraud', weight: 50 })
    score += 50
  }
  const trimmed = sender.trim()
  if (trimmed.startsWith('+') && !trimmed.replace(/\s/g, '').startsWith('+91')) {
    flags.push({ id: 'intl', label: 'International sender number', weight: 15 })
    score += 15
  } else if (digits.length === 10 && !/^[6-9]/.test(digits)) {
    flags.push({ id: 'odd', label: 'Unusual mobile number format', weight: 10 })
    score += 10
  }
  return { flags, score }
}

export function analyzeMessage({ message, sender }) {
  return new Promise((resolve) => {
    // Simulate network latency so loading states are visible.
    setTimeout(() => {
      const flags = RULES.filter((r) => r.pattern.test(message)).map(({ id, label, weight }) => ({ id, label, weight }))
      let score = flags.reduce((s, f) => s + f.weight, 0)

      const s = senderFlags(sender)
      flags.push(...s.flags)
      score += s.score

      const numbers = [...new Set((message.match(PHONE_RE) || []).map((n) => n.trim()))]
      const links = [...new Set(message.match(URL_RE) || [])]

      numbers.forEach((n) => {
        if (REPORTED_NUMBERS.has(normalizeNumber(n))) {
          flags.push({ id: 'reported-in-msg', label: `Number ${n} reported as fraud`, weight: 40 })
          score += 40
        }
      })

      score = Math.min(100, score)
      const verdict = score >= 60 ? 'fraud' : score >= 30 ? 'suspicious' : 'safe'

      resolve({
        id: Date.now(),
        checkedAt: new Date().toISOString(),
        message,
        sender: sender || null,
        score,
        verdict,
        flags,
        numbers,
        links,
      })
    }, 900)
  })
}

export const SAMPLE_MESSAGES = [
  {
    title: 'Bank KYC scam',
    sender: '+44 7700 900123',
    message:
      'Dear Customer, your SBI account will be BLOCKED today due to pending KYC. Update immediately: http://bit.ly/sbi-kyc-upd or call 9876543210. Do not share with anyone.',
  },
  {
    title: 'Card OTP scam',
    sender: '8001234567',
    message:
      'Your credit card reward points worth Rs 4,999 expire tonight. Share the OTP sent to your number to redeem cashback instantly.',
  },
  {
    title: 'Genuine message',
    sender: '',
    message: 'Hi! Are we still meeting at 6 for dinner? Let me know if the plan changes.',
  },
]
