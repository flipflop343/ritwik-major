# FraudShield – Frontend

React + Vite UI for checking whether a message or sender number is fraudulent.

## Run

1. Install Node.js 18+ from https://nodejs.org
2. In this folder:

```bash
npm install
npm run dev
```

The app opens at http://localhost:5173

## Structure

```
src/
  App.jsx                  page layout + state (result, history)
  components/
    Header.jsx
    MessageChecker.jsx     message + sender input form, samples
    ResultCard.jsx         verdict, risk gauge, red flags, tips
    HistoryList.jsx        last 10 checks (localStorage)
    Features.jsx           live / coming-soon features
  utils/analyzer.js        TEMPORARY rule-based analyzer
```

## Connecting the backend later

`analyzeMessage({ message, sender })` in `src/utils/analyzer.js` is the only
function the UI calls. Replace its body with a `fetch` to your API and return the
same shape:

```js
{ id, checkedAt, message, sender, score /*0-100*/, verdict /*'fraud'|'suspicious'|'safe'*/,
  flags: [{ id, label, weight }], numbers: [], links: [] }
```
