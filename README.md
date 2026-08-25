# Fictoshop Storefront (Django)

Sports-focused storefront implemented with Django and vanilla frontend assets. The UI mirrors the original FastAPI demo but now follows Django best practices with reusable templates, modular CSS, and a simple in-memory cart backed by database products.

## Project structure

```
├── assets/                # Frontend assets (CSS/JS/images)
├── images/uploads/        # Media uploaded via Django admin (product photos)
├── shop/
│   ├── templates/shop/
│   │   ├── base.html      # Shared layout (header/footer/global chrome)
│   │   └── index.html     # Storefront homepage extending the base
│   ├── models.py          # Product model
│   ├── serializers.py     # DRF serializers for API endpoints
│   ├── storefront.py      # In-memory cart logic
│   ├── views.py           # API views + login/logout endpoints
│   └── urls.py            # App routes
└── manage.py
```

## Prerequisites

- Python 3.12 (matching the repo's runtime)
- pip / virtualenv or Conda

## Local setup

```bash
# Create virtual environment (example using venv)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations and seed the database
python manage.py migrate
python manage.py loaddata shop/fixtures/products.json  # optional seed

# Run the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to see the storefront. The Django admin lives at `/admin/`; make sure to create a superuser and upload product images there (they're stored under `images/uploads/`).

## Mobile bundles

- The mobile web bundle lives in `mobile-web/` (HTML + assets). iOS references it directly via Xcode; Android needs a copy in `app/src/main/assets/`.
- To sync into Android assets: from repo root run `bash scripts/sync-mobile-web.sh`. Rebuild the Android app afterward.
- Set the API base in `mobile-web/index.html` via `data-api-base`. For Android emulator, use `http://10.0.2.2:8000`. For iOS simulator, use `http://127.0.0.1:8000` or your Mac's LAN IP if testing on device.

## iOS app (WKWebView)

- Project lives in `ios-app/`. The app loads the bundled `mobile-web` folder via a folder reference.
- Dev HTTP: ATS exceptions are enabled in the project. Point `data-api-base` to a reachable host for your simulator/device (e.g., LAN IP for real device).
- Build/run from Xcode; the bottom bar provides back/reload/forward.

## Android app (WebView)

- Project lives in `android-app/`. The WebView loads `file:///android_asset/index.html`.
- Before building, sync `mobile-web/` into `app/src/main/assets/` using `bash scripts/sync-mobile-web.sh`.
- Dev HTTP: manifest allows cleartext + INTERNET permission. For local backend, start Django and use `http://10.0.2.2:8000` as `data-api-base`.

## Frontend workflow

- Global styles live in `assets/css/index.css`. Components (hero, catalog, cart) are grouped by section, and reusable colors/spacing tokens are defined under `:root`.
- `shop/templates/shop/base.html` contains global chrome. Individual views (`index.html`, login, product detail, etc.) only worry about their unique content blocks.
- `assets/js/storefront.js` powers filters, cart interactions, and hero stats. The script expects the `data-api-base` attribute on the `<body>` element and the toast container present in `index.html`.

## Testing

Current project uses Django's default test runner. To execute any written tests:

```bash
python manage.py test
```

Add unit tests under `shop/tests.py` as you add new behavior.

## End-to-end tests (Playwright + pytest-bdd)

- Install deps: `python -m pip install -r playwright_tests/requirements.txt`
- Install browser runtime: `python -m playwright install chromium`
- Run the Django server locally (default `http://127.0.0.1:8000`)
- Execute tests headless: `pytest playwright_tests`
- Headed mode: `pytest playwright_tests --headed`

## Conventions

- Use Django templates + `{% static %}` for asset references.
- Keep media uploads inside `images/uploads/` so `MEDIA_URL` serves them automatically.
- When adding new pages, prefer extending `shop/base.html` to keep navigation and global styles consistent.
