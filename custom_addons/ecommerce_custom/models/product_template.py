from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_featured = fields.Boolean(
        string="Featured on Homepage",
        default=False,
        index=True,
        help="Show this published product in the homepage featured section.",
    )
    is_promotional = fields.Boolean(
        string="Promotional Product",
        default=False,
        index=True,
        help="Include this product in the promotional homepage section.",
    )
    promotion_label = fields.Char(
        string="Promotion Label",
        help="Short promotional label shown on the product card.",
    )
