# Project layout

```
fictoshop/                   # Repo root
├── mobile-web/              # Canonical bundled web assets for mobile (HTML/CSS/JS/images)
├── ios-app/                 # iOS WKWebView shell that references mobile-web via folder reference
├── android-app/             # Android WebView shell; assets copied in from mobile-web
├── shop/                    # Django app (views, models, templates, API)
├── assets/                  # Frontend assets used by the Django-rendered web app
├── images/                  # Uploaded media (served by Django)
├── manage.py                # Django entry point
└── scripts/                 # Utility scripts (e.g., syncing mobile-web into Android assets)
```

Notes:
- **mobile-web** is the single source of truth for the mobile bundle. iOS consumes it via an Xcode folder reference; Android needs it copied into `app/src/main/assets/`.
- **android-app** should run the sync script before building so the latest mobile-web files land in `app/src/main/assets/`.
- Backend runs on Django; ensure CORS/cleartext settings are aligned with your dev environment (10.0.2.2 for Android emulator, 127.0.0.1 or LAN IP for iOS simulator/device).
