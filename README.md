# Password Strength Analyzer

## Overview

Password Strength Analyzer V2 is an educational Flask application for exploring three related security questions:

1. **Analyze:** How technically strong does a password appear?
2. **Personalized Analysis:** Does basic information about its owner make it easier to predict?
3. **Generate:** What would a stronger random password or memorable passphrase look like?

The project uses a small, readable analysis engine rather than presenting an opaque cracking-time prediction. It has no database, telemetry, tracking, third-party APIs, or browser storage.

![Password Strength Analyzer dashboard](docs/screenshots/dashboard.png)

> The screenshot path is a portfolio placeholder. The application does not depend on this file.

## Features

- Technical password analysis with a deterministic score from 0 to 100
- Separate personal-predictability risk and personalized assessment
- Secure random password generation with configurable character sets
- Memorable passphrase generation from independently selected local words
- Simplified character-pool entropy estimation
- Common-password, weak-word, sequence, repetition, and year detection
- Contextual security recommendations
- Accessible tabs, labeled controls, keyboard navigation, and visible focus states
- Responsive professional dark interface using HTML, CSS, and vanilla JavaScript
- Strict Flask JSON validation, request-size limits, secure headers, and no secret echo
- Automated pytest coverage for analysis, personalized risk, generation, privacy, and APIs

## Why Personalized Analysis?

A password can satisfy common composition rules and still be predictable to someone targeting a specific person. For example, `Sarah2004!` contains uppercase and lowercase letters, numbers, and a symbol, but an attacker who knows Sarah's name and birth year has a much smaller search space.

Personalized mode accepts only optional, basic fields: first name, last name, username/handle, birth year, and up to five keywords. It looks for conservative, obvious relationships such as name + year, username fragment + number, or a predictable symbol suffix. It does not profile identities, build attack wordlists, or ask for addresses, phone numbers, full dates of birth, identifiers, or security-question answers.

## Scoring Model

### Technical score

The main score combines positive evidence and then subtracts predictable-pattern penalties:

| Signal | Score effect |
| --- | ---: |
| Length | Up to +48 |
| Character diversity | +4 per used class, up to +16 |
| Theoretical entropy | Up to +34 |
| Exceptional variety bonus | +2 |
| Exact common password | -55 |
| Embedded weak words | -12 each, capped at -24 |
| Predictable sequence | -12 |
| Repeated character or short block | -15 |
| Four-digit year | -5 |

Length credit rises in stages. A mixed, random-looking 16-character password generally reaches around 80 and 20+ clean random characters can reach the 90s. The final two points require at least 36 characters, all four character classes, at least 200 estimated bits, no detected patterns, and at least 60% distinct case-folded characters. This explicit variety rule keeps typical long word phrases below 100 while making 100 possible without unrealistic 100-character inputs.

Entropy is estimated as:

```text
password length × log2(inferred character pool size)
```

This is a theoretical character-pool estimate, not measured randomness and not an exact cracking-time forecast. Pattern penalties remain active even when the estimate is high. Every score is rounded and clamped to `0–100`.

Strength labels remain:

- 0–19: Very Weak
- 20–39: Weak
- 40–59: Medium
- 60–79: Strong
- 80–100: Very Strong

Within the top label, 80–89 is very strong, 90–97 is excellent, and 98–100 is exceptional according to this limited analyzer—not a guarantee of safety.

### Personal predictability

Personalized mode always displays the unchanged technical score separately. It then applies explicit personal-risk penalties:

| Personal signal | Penalty |
| --- | ---: |
| First or last name match | -16 each |
| Username fragment | -14 |
| Birth year | -12 |
| One or more personal keywords | -12 |
| Personal token + year | -10 |
| Personal token + other number | -6 |
| Predictable symbol suffix | -5 |
| Password dominated by matched personal data | -10 |

The personal penalty is capped at 60. Risk bands are Low (0), Moderate (1–18), High (19–34), and Critical (35+). The personalized assessment is:

```text
max(0, technical score − personal-risk penalty)
```

It can never exceed the technical score. Matching is case-insensitive, ignores simple separators for names, and considers meaningful username fragments of at least three characters. A two-digit birth-year suffix is considered only when a personal token also matches, reducing false positives. These are deliberately conservative heuristics.

## Password Generator

### Random password mode

Random mode uses Python's `secrets` module, not `random` or `Math.random()`. It supports 12–64 characters and configurable uppercase, lowercase, digits, and symbols. At least one set is required, and each enabled set is guaranteed to appear. The remaining characters and final order are selected with operating-system-backed cryptographic randomness.

### Memorable passphrase mode

Passphrase mode independently selects 3–6 unrelated words using `secrets.choice`. The default uses five words, capitalization, a random two-digit number, and a random symbol. Separators are configurable.

The local vocabulary contains exactly 256 familiar, neutral words, so each independent word selection contributes 8 bits and five words contribute 40 bits before optional random additions. Capitalization and separators are formatting choices and are not counted as random entropy. The generator reports this selection estimate transparently; a larger Diceware-style list would provide more entropy per word.

Every generated value is automatically evaluated by the same `src.analyzer.analyze_password` function used by Analyze. The UI offers Copy, Regenerate, and Analyze actions. Generated values remain only in transient page/server memory and the clipboard when the user explicitly selects Copy.

## Security & Privacy

The browser sends manually entered passwords to the same-origin Flask API over the deployment's HTTP connection. Personalized mode also sends the optional profile fields to `POST /api/analyze/personalized`. Flask validates them, compares them in request memory, returns only generic derived findings, and retains nothing. Use HTTPS in production.

Random passwords and passphrases are generated in Flask request memory and necessarily returned in their explicitly requested generator response. They are then analyzed by the same in-memory engine.

- No values are written to a database or files.
- No values are put in cookies, sessions, `localStorage`, or `sessionStorage`.
- No request-body, password, profile, or generated-value logging exists in application code.
- No analytics, telemetry, remote fonts, breach APIs, or other third parties are used.
- API and page responses use `Cache-Control: no-store`.
- Password/profile form fields are cleared after each analysis.

Hosting platforms and reverse proxies may keep ordinary access metadata. Operators must keep request-body logging disabled. See the full [threat model and data flow](docs/SECURITY.md).

## API

All endpoints accept JSON and return structured JSON:

| Endpoint | Purpose |
| --- | --- |
| `POST /api/analyze` | Technical analysis; never echoes the submitted password |
| `POST /api/analyze/personalized` | Technical + personal-risk analysis; never echoes inputs |
| `POST /api/generate/random` | Secure random generation plus technical analysis |
| `POST /api/generate/passphrase` | Secure passphrase generation plus technical analysis |

Passwords are non-empty strings limited to 256 characters. Personal names and usernames are limited to 64 characters, birth year to 1900–2099, and keywords to five values of at most 32 characters. Request bodies are limited to 4 KiB. Generator output endpoints include the generated password by design; analysis endpoints do not.

Example:

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"password":"example-only-Cobalt!47"}'
```

Do not demonstrate password tools with a real account password.

## Tech Stack

- Python 3, Flask, and the standard-library `secrets` module
- HTML5, CSS3, and vanilla JavaScript
- pytest
- Gunicorn

## Installation and Local Use

Linux and macOS:

```bash
git clone <repository-url>
cd password-strength-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows PowerShell:

```powershell
git clone <repository-url>
cd password-strength-analyzer
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open [http://localhost:5000](http://localhost:5000).

## Running Tests

```bash
pytest
python -m compileall -q app.py src tests
node --check static/js/app.js
```

## Project Structure

```text
.
├── app.py
├── Procfile
├── pytest.ini
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── generator.py
│   ├── patterns.py
│   ├── personalized.py
│   ├── recommendations.py
│   ├── scoring.py
│   └── words.py
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/index.html
├── tests/
│   ├── test_analyzer.py
│   ├── test_api_v2.py
│   ├── test_generator.py
│   ├── test_patterns.py
│   ├── test_personalized.py
│   └── test_scoring.py
└── docs/SECURITY.md
```

## Screenshots

Portfolio captures can be stored at:

- `docs/screenshots/dashboard.png`
- `docs/screenshots/personalized.png`
- `docs/screenshots/generator.png`
- `docs/screenshots/mobile.png`

## Deployment

The existing `Procfile` runs `gunicorn app:app`, which is compatible with Render and Railway. Both can supply `PORT`. For another host:

```bash
gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
```

Deploy behind HTTPS. HSTS is emitted only for requests Flask recognizes as HTTPS, so local HTTP remains usable. Keep debug mode and proxy request-body logging disabled.

## Limitations

- No breached-password database is queried.
- Common-password, weak-word, and passphrase dictionaries are intentionally limited and local.
- Entropy estimates are approximate and can overstate human-created passwords.
- Personal-risk detection is heuristic and cannot know what information an attacker actually has.
- Normalization is conservative and does not cover every substitution, nickname, script, or language.
- The 256-word generator vocabulary is smaller than a full Diceware list.
- Security also depends on uniqueness, storage, authentication controls, hashing, rate limits, and multi-factor authentication.
- A hosted server sees submitted values briefly in process memory; transport privacy depends on HTTPS and trusted hosting.

## Future Improvements

- Broader versioned dictionaries with documented provenance
- Optional client-side analysis build to reduce server-memory exposure
- More internationalized normalization and keyboard-layout checks
- CI workflows for tests, formatting, and dependency scanning
- A larger audited passphrase vocabulary

## Educational Purpose

This project is designed to stay understandable enough for a cybersecurity student to audit and explain. It demonstrates why composition rules alone are insufficient: length helps, predictable structure hurts, personal information changes targeted risk, and independently randomized passphrases can balance memorability with security.
