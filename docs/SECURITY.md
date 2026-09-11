# Security Policy and Design

## Scope

Password Strength Analyzer V2 is an educational assessment and generation tool. It is not an authentication service, password manager, breach monitor, identity profiler, secret store, or guarantee of password safety.

## Threat Model

Sensitive assets are:

- A submitted password while it exists in the browser, network request, and Flask request memory
- Optional first name, last name, username, birth year, and personal keywords during personalized analysis
- A generated password/passphrase while it exists in Flask response memory, the browser DOM, and—only after an explicit Copy action—the system clipboard

Relevant threats include accidental logging or persistence, insecure transport, third-party disclosure, reflected values, oversized-input resource use, debug output, browser storage, response caching, cross-site framing, malicious script execution, and targeted guesses based on public personal information.

The application assumes the browser, host operating system, Python runtime, deployment account, and TLS termination are trusted. A compromised browser, server process, host, extension, clipboard manager, or reverse proxy is outside its protection boundary.

## Data Flow

### Technical analysis

1. The browser sends the password in a JSON body to same-origin `POST /api/analyze`.
2. Flask validates a non-empty string of at most 256 characters.
3. The analyzer derives length, character classes, theoretical entropy, predictable patterns, score, issues, and recommendations in memory.
4. Flask returns only derived findings. The password is never returned.
5. The frontend clears its password field after completion.

### Personalized analysis

1. The browser sends the password and only the optional profile fields the user supplied to same-origin `POST /api/analyze/personalized`.
2. Flask enforces field, keyword-count, year, password, and request-body limits.
3. The normal technical analyzer runs unchanged.
4. A separate conservative heuristic layer performs case-insensitive, separator-tolerant personal matching in request memory.
5. Flask returns the technical findings, generic matched-field categories, generic pattern explanations, penalty explanations, risk band, and adjusted score. It returns none of the original password/profile values.
6. The frontend resets every password and profile form field after completion.

Personal profile processing is server-side, not browser-only. In production, HTTPS is required to protect both password and profile data in transit.

### Random password generation

1. The browser sends options—not personal information—to `POST /api/generate/random`.
2. Flask uses Python's `secrets` module and operating-system randomness.
3. The value is analyzed by the same technical engine.
4. The requested generated value, derived analysis, and generation estimate are returned.

### Passphrase generation

1. The browser sends word count and formatting options to `POST /api/generate/passphrase`.
2. Flask independently selects words from a fixed 256-word local vocabulary with `secrets.choice`; optional number and symbol choices also use `secrets`.
3. No personalized-analysis values are read or reused.
4. The value is analyzed by the main engine and explicitly returned with derived metadata.

Generator endpoints necessarily include the generated value because that is their purpose. Analyzer endpoints never echo submitted passwords.

## Data Minimization

All personalized fields are optional. The application asks for a four-digit birth year rather than a full birth date and does not request addresses, phone numbers, family details, government identifiers, account recovery answers, or other invasive information. Input limits are:

- Password: 256 characters
- First name, last name, username: 64 characters each
- Birth year: one year from 1900 through 2099
- Keywords: no more than 5, each at most 32 characters
- Total JSON request: 4 KiB

## Data Retention

None. The application has:

- No database or secret files
- No application sessions containing user input
- No password/profile cookies
- No `localStorage` or `sessionStorage`
- No service worker or offline cache
- No analytics, telemetry, tracking pixels, or error-reporting SDK
- No third-party password or breach API

Values remain referenced only as needed for the active request or displayed generator result. Python and JavaScript runtimes control memory reclamation, so immediate physical erasure cannot be guaranteed. The operating-system clipboard is outside the application and receives a value only when the user selects Copy.

## Logging

Application code contains no logging or printing of passwords, profile fields, JSON bodies, or generated values. Errors are fixed generic messages and never interpolate submitted data.

Ordinary web-server access logs may contain routes, response status, IP address, user agent, and timing metadata. Sensitive values are carried in JSON bodies, not URLs. Deployment operators must not enable request-body capture in Gunicorn configuration, reverse proxies, hosting dashboards, monitoring agents, tracing tools, or exception-reporting middleware.

## Browser Storage and Caching

No browser persistence API is used. Every response includes `Cache-Control: no-store, max-age=0`. The frontend keeps current values only in form controls or short-lived JavaScript variables needed for a request/display. Analysis forms are reset after completion. Generated output remains visible in the current DOM so it can be copied or analyzed, but it is never saved across navigation or reload.

## Third Parties

None. Scripts, styles, fonts, word lists, and analysis data are local to the application. The Content Security Policy permits scripts, styles, images, and connections only from the same origin (with data images allowed) and blocks objects and framing.

## Personalized Threat Model

A targeted attacker may know public or easily discovered information such as a name, online handle, approximate age, interests, team, or pet nickname. Human-created passwords often combine these tokens with capitalization, numbers, years, or a trailing symbol.

The personalized layer detects only obvious relationships. It does not query social networks, enrich identity data, create attack wordlists, attempt password cracking, or infer undisclosed information. Its adjusted score represents an educational penalty for detected construction patterns—not a probability that a specific attacker will guess the password.

## Security Controls

- JSON object validation and explicit type/range/length checks
- 4 KiB request-body limit and 256-character password limit
- Generic errors that do not reflect submitted values
- Deterministic scores clamped to 0–100
- Cryptographically secure generation through `secrets`
- Technical analysis shared by manually entered and generated passwords
- Flask debug mode disabled unless explicitly enabled for local development
- Gunicorn production entry point
- `Cache-Control: no-store`
- Restrictive Content Security Policy
- Clickjacking, MIME-sniffing, referrer, and unnecessary-feature restrictions
- HSTS for requests recognized as HTTPS
- Random process-local Flask secret because no user session is used; deployments may set `SECRET_KEY`

## Deployment Guidance

- Serve only over HTTPS in production.
- Keep Flask debug mode disabled.
- Ensure the proxy forwards the original HTTPS scheme correctly if HSTS behavior depends on it.
- Disable request-body logging, tracing capture, and automatic form/session replay.
- Restrict access to platform logs and configuration.
- Keep Python and pinned dependencies patched.
- Apply resource limits and edge rate limiting for public deployments.

## Limitations

- The entropy figure is a theoretical character-pool approximation, not observed randomness.
- The analyzer cannot identify every weak word, leaked password, language, keyboard layout, substitution, or repeated semantic pattern.
- Personalized matching cannot know what an attacker knows and intentionally avoids aggressive transformations that would increase false positives.
- The 256-word passphrase vocabulary provides 8 bits per selected word; it is smaller than full Diceware lists.
- A hosted server can inspect plaintext values in request/process memory.
- TLS and platform logging behavior are deployment responsibilities.
- Browser history is not used for values, but clipboard managers or browser extensions may observe displayed/copied secrets.
- No application-level rate limiting is included; public deployments should apply it at the edge.
- Generated or highly scored passwords still need to be unique and protected by sound storage and authentication practices.

## Reporting a Vulnerability

Open a private security advisory in the GitHub repository rather than publishing sensitive details in a public issue. Include reproduction steps, impact, and a suggested mitigation when possible. Never include real passwords, credentials, or personal data.
