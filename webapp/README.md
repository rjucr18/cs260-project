# webapp

Flask-based demo application providing an HTTP interface to generate and compare secure vs vulnerable code outputs.

Contents:
- `app.py`: Flask factory + endpoints. `/generate` accepts JSON or form data with prompt and mode (`secure`, `vulnerable`, `both`). Lazy-loads model wrappers on first request.
- `templates/index.html`: Minimal client UI performing async POST requests and rendering side-by-side results.

Endpoints:
- `GET /` : Serves the HTML template UI.
- `POST /generate` : Body keys: `prompt` (required), `mode` (default `both`), `max_length`, `temperature`.

Usage:
```powershell
python -m webapp.app
# Visit http://localhost:5000
```

Notes:
- Designed for qualitative comparison; not hardened for production traffic.
- Add rate limiting / input sanitation before any public exposure.
- Future: integrate CodeQL scan trigger and result visualization.
