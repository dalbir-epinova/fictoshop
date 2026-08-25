# Fictoshop Storefront

Fictoshop is a Django storefront with a vanilla HTML, CSS, and JavaScript frontend. It includes a product catalog, reviews, a persistent floating cart, checkout with shipping details, stored orders, an order confirmation page, and Django administration.

## Main features

- Product catalog with search, sorting, stock status, and product details
- Product reviews for signed-in users
- Floating cart that remains visible while it contains products
- Checkout form for customer and shipping information
- Persistent orders and order-item snapshots in SQLite
- Stock reduction after a successful order
- Session-protected order confirmation page
- Django admin for products and orders
- Django unit and integration tests
- Playwright browser tests written in Python

## Project structure

```text
assets/                 Frontend CSS, JavaScript, and images
fictoshop_django/       Django project settings and root URLs
images/uploads/         Product images uploaded through Django admin
mobile-web/             Web bundle used by the mobile applications
playwright-python/      Playwright end-to-end tests using pytest
shop/                   Storefront Django application
  migrations/           Database migrations
  templates/shop/       Django templates
  admin.py              Product and order administration
  forms.py              Checkout form
  models.py             Products, reviews, orders, and order items
  storefront.py         In-memory cart logic
  tests.py              Unit and integration tests
  views.py              Pages and API endpoints
manage.py               Django command-line entry point
requirements.txt        Python dependencies for the complete project
```

## Prerequisites

- Python 3.12
- pip
- Git Bash, PowerShell, or another terminal

## Local setup with Git Bash on Windows

From the project root, create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/Scripts/activate
```

Install all backend and testing dependencies:

```bash
python -m pip install -r requirements.txt
```

Apply database migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in a browser.

## Demo data and administration

After migrations, the development bootstrap creates sample products when the catalog is empty. It also creates a development superuser if no superuser exists.

Default development credentials:

```text
Username: admin
Password: admin123
```

Open <http://127.0.0.1:8000/admin/> to manage products and view orders. Do not use the default credentials in a deployed environment. They can be overridden before migration with `FICTOSHOP_ADMIN_USER` and `FICTOSHOP_ADMIN_PASSWORD`.

To create another superuser interactively:

```bash
python manage.py createsuperuser
```

## Storefront and checkout

The cart is maintained in memory for this demo application. When it contains products, a compact cart appears at the bottom-right of the storefront and stays visible while the page scrolls.

Checkout collects the customer's name, email, telephone number, and shipping address. A successful checkout:

1. Creates an `Order` in the `orders` database table.
2. Creates an `OrderItem` snapshot for every cart line.
3. Reduces product stock.
4. Clears the cart.
5. Redirects the customer to a session-protected confirmation page.

Because the cart is currently stored in application memory, it is intended for local development and demonstration rather than production deployment.

## Django tests

Run the unit and integration tests with Django's test runner:

```bash
python manage.py test
```

The tests use a temporary test database and do not modify `db.sqlite3`.

## Playwright tests

Playwright tests are located in `playwright-python/` and use Python with pytest.

Install the Chromium browser runtime once:

```bash
python -m playwright install chromium
```

Start Django in one terminal:

```bash
python manage.py runserver
```

In a second terminal, activate the same virtual environment and run Playwright headlessly:

```bash
python -m pytest playwright-python
```

To display the browser during the test:

```bash
python -m pytest playwright-python --headed
```

The tests use `http://127.0.0.1:8000` by default. Set `FICTOSHOP_BASE_URL` to target a different environment.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/products` | List products |
| `GET` | `/products/<id>` | Retrieve one product |
| `POST` | `/cart` | Add a product to the cart |
| `GET` | `/cart` | Retrieve the cart |
| `DELETE` | `/cart/<id>` | Remove a cart line |
| `DELETE` | `/cart` | Clear the cart |
| `GET`, `POST` | `/checkout` | Display or submit shipping details |

## Mobile bundles

- The shared mobile web bundle is located in `mobile-web/`.
- Android loads it from `android-app/app/src/main/assets/`.
- Synchronize the bundle with `bash scripts/sync-mobile-web.sh` before rebuilding Android.
- Use `http://10.0.2.2:8000` for the Android emulator API base.
- iOS can use `http://127.0.0.1:8000` in the simulator or the computer's LAN address on a physical device.

## Development conventions

- Extend `shop/templates/shop/base.html` when adding pages.
- Keep shared styles in `assets/css/index.css`.
- Keep storefront behavior in `assets/js/storefront.js`.
- Store uploaded product media under `images/uploads/`.
- Add backend tests to `shop/tests.py` and browser tests to `playwright-python/`.
# fictoshop 
