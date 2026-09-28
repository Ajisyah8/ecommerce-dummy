# Odoo Community E-Commerce

Odoo Community 19.0 e-commerce project using the official Odoo repository and PostgreSQL.

## Current scope

This initial implementation provides the project bootstrap:

- Official Odoo `19.0` source in `odoo/`.
- PostgreSQL 16 through Docker Compose.
- Runtime configuration from `.env`.
- Read-only mounts for Odoo source and custom addons.
- Initial `ecommerce_custom` addon skeleton.
- Community e-commerce homepage at `/ecommerce/home` with featured, promotional, new products, and categories.
- Server-side cart stock validation through the native `sale.order` cart hook.

Business features will be added incrementally on top of native `website_sale`, `sale`, `product`, `stock`, `delivery`, `payment`, and `portal` modules.

After installing `ecommerce_custom`, set the Website homepage URL to `/ecommerce/home` if this custom homepage should be the public root page.

Cart quantity updates for storable and consumable products are checked against the current warehouse `free_qty`. If the requested quantity exceeds available stock, the native cart response receives a warning and the quantity is capped. Service products are not stock-limited.

## Checkout and shipping

Checkout continues to use the native `/shop/checkout`, `/shop/address`, `/shop/delivery`, and `/shop/payment` flow. Before payment and again before sales order confirmation, the cart is rechecked against current warehouse stock.

Shipping methods are configured through the native Delivery Methods menu. Flat-rate shipping uses a fixed delivery price, free shipping uses the free-over threshold, and weight/order rules use Odoo delivery price rules. External carriers remain optional modules and are not part of the Community baseline.

## Customer account

Customer registration, login, profile updates, address management, order history, and order detail use the native `auth_signup`, `portal`, and `sale` flows. The order list is restricted to the authenticated user's commercial partner hierarchy, and portal order detail uses Odoo's document access/token checks. The custom portal layer only adds order, payment, and shipping status presentation.

## Payment architecture

The baseline payment provider is Odoo Community's native `payment_custom` module with provider code `custom` and mode `wire_transfer`. It uses the standard `payment.provider` and `payment.transaction` models. Bank details are configured through Odoo company bank journals; credentials and bank account data are not stored in custom code.

Enable and configure it from Website > Configuration > Payment Providers after setting up the company's bank journal. The Demo provider may be installed only for development testing. Midtrans, Xendit, and other gateways must be added later as separate provider modules and are not dependencies of this baseline.

## SEO

Odoo Community's native Website layer remains responsible for `robots.txt`, sitemap, canonical URLs, editable meta title/description/keywords, and Open Graph defaults. The custom module enhances product metadata with `og:type=product`, SKU metadata, and JSON-LD availability based on live stock (`InStock` or `OutOfStock`).

## Frontend and accessibility

The custom frontend layer keeps native Website Sale header, search, account, and cart components. It adds a responsive footer, keyboard-accessible skip navigation, visible focus states, mobile-first spacing, and accessible navigation labels without replacing native checkout interactions.

## Security and tests

The project relies on Odoo's native portal access CSV and record rules for `sale.order` and `sale.order.line`. The Community portal rule restricts records to `user.commercial_partner_id` and its child contacts. Custom controllers do not expose order IDs or customer data without native portal access checks. Regression tests cover customer order isolation, native rule scope, product merchandising fields, and native Wire Transfer availability.

## Prerequisites

- Git
- Node.js 20+ and npm
- Python 3.12+
- PostgreSQL 16+ running locally

## Setup

```powershell
Copy-Item .env.example .env
# Edit .env and replace both passwords.
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r odoo\requirements.txt
npm run odoo
```

The native workflow runs `odoo/odoo-bin` directly. PostgreSQL must already be running on `localhost:5432`. On the first run, create a database from Odoo's database manager using the `ODOO_ADMIN_PASSWORD` from `.env`; then stop Odoo with `Ctrl+C`, install the modules, and start it again:

```powershell
npm run init -- base,web,website,website_sale,payment_custom,ecommerce_custom
npm run odoo
```

If PowerShell blocks activation, run `.\.venv\Scripts\python.exe -m pip install -r odoo\requirements.txt` and set `ODOO_PYTHON` to that executable in `.env`.

## Database migration

The database is PostgreSQL-backed and module migrations use Odoo's native `--update` mechanism. Start PostgreSQL and create the database first, then run:

```powershell
npm run migrate
```

To install modules into a new database during initialization:

```powershell
npm run init -- base,web,website_sale,payment_custom,ecommerce_custom
```

To migrate specific modules:

```powershell
npm run migrate -- ecommerce_custom
```

The same workflow can be run through npm:

```powershell
npm run odoo
npm run migrate
npm run migrate -- website_sale,ecommerce_custom
```

On Windows PowerShell systems that block `npm.ps1`, use the equivalent `npm.cmd run <script>` or run the commands from Command Prompt/Git Bash. This is an execution-policy issue, not an application dependency.

Migration runs with Odoo's native `--stop-after-init` option. It does not modify the Odoo source checkout.

Docker Compose remains available as an optional isolated environment, but it is not required for local development.

## Community-only rule

The only Odoo source allowed is the official `odoo/odoo` repository on branch `19.0`. No Enterprise repository or Enterprise addons may be added to `addons_path`.

## Development workflow

```powershell
python odoo/odoo-bin --config=.odoo-runtime/odoo.conf
docker compose exec odoo python /mnt/odoo/odoo-bin --help
docker compose down
```

Custom code belongs only in `custom_addons/`. Do not edit `odoo/odoo/` or `odoo/addons/`.
