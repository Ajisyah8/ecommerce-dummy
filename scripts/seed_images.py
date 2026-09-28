"""Attach local realistic catalog photos to demo products through Odoo ORM."""

import base64
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
image_dir = ROOT / "custom_addons" / "ecommerce_custom" / "static" / "src" / "img" / "products"
product_assets = {
    "EC-TSH-001": ("ec-tshirt.png", "Navy Essential Tee"),
    "EC-SNK-002": ("ec-sneakers.png", "Sage Canvas Sneakers"),
    "EC-TOT-003": ("ec-tote.png", "Terra Carry Tote"),
    "EC-HOM-101": ("ec-lamp.png", "Arc Halo Desk Lamp"),
    "EC-HOM-102": ("ec-coffee.png", "Speckled Morning Cup"),
    "EC-TEC-201": ("ec-speaker.png", "Orbit Wireless Speaker"),
    "EC-TEC-202": ("ec-organizer.png", "Walnut Modular Organizer"),
    "EC-WEL-301": ("ec-candle.png", "Sandalwood No. 01 Candle"),
    "EC-WEL-302": ("ec-care.png", "Daily Ritual Care Set"),
}

with Registry(database).cursor() as cursor:
    env = api.Environment(cursor, SUPERUSER_ID, {})
    products = env["product.template"].search([("default_code", "like", "EC-%")])
    updated = 0
    for product in products:
        image_file, product_name = product_assets[product.default_code]
        image_path = image_dir / image_file
        product.name = product_name
        product.image_1920 = base64.b64encode(image_path.read_bytes())
        updated += 1
    cursor.commit()
    print(f"Attached realistic catalog photos to {updated} demo products.")
