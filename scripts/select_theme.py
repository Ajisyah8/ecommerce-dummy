"""Select an installed or available Community website theme through Odoo ORM."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "odoo"))

import odoo  # noqa: E402
from odoo import SUPERUSER_ID, api  # noqa: E402
from odoo.modules.registry import Registry  # noqa: E402
from odoo.tools import config  # noqa: E402


database = sys.argv[1]
theme_name = sys.argv[2]
config_path = sys.argv[3]
config.parse_config([f"--config={config_path}", "-d", database])

with Registry(database).cursor() as cursor:
    env = api.Environment(cursor, SUPERUSER_ID, {})
    theme = env["ir.module.module"].search([("name", "=", theme_name)], limit=1)
    if not theme:
        raise SystemExit(f"Theme not found: {theme_name}")
    theme.button_choose_theme()
    cursor.commit()
    website = env["website"].get_current_website()
    print(f"Active theme: {website.theme_id.name}")
