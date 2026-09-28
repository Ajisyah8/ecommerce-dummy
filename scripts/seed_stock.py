"""Seed inventory for the demo catalog through Odoo's inventory API."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "odoo"))

import odoo  # noqa: E402
from odoo import SUPERUSER_ID, api  # noqa: E402
from odoo.modules.registry import Registry  # noqa: E402
from odoo.tools import config  # noqa: E402


database = sys.argv[1]
config_path = sys.argv[2]
config.parse_config([f"--config={config_path}", "-d", database])

with Registry(database).cursor() as cursor:
    env = api.Environment(cursor, SUPERUSER_ID, {})
    warehouse = env["stock.warehouse"].search([], limit=1)
    products = env["product.product"].search([("default_code", "like", "EC-%")])
    if not warehouse:
        raise SystemExit("No warehouse found. Install Inventory first.")
    if not products:
        raise SystemExit("No demo products found. Run npm run migrate -- ecommerce_custom first.")

    products.write({"is_storable": True})
    quants = env["stock.quant"].with_context(inventory_mode=True)
    for product in products:
        quants.create({
            "product_id": product.id,
            "location_id": warehouse.lot_stock_id.id,
            "inventory_quantity_auto_apply": 25,
        })
    cursor.commit()
    print(f"Seeded 25 units for {len(products)} demo products in {warehouse.name}.")
