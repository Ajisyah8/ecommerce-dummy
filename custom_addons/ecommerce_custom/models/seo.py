from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _default_website_meta(self):
        values = super()._default_website_meta()
        self.ensure_one()
        if self.default_code:
            values["default_opengraph"]["product:retailer_item_id"] = self.default_code
        values["default_opengraph"]["og:type"] = "product"
        return values


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _to_markup_data(self, website):
        markup_data = super()._to_markup_data(website)
        self.ensure_one()
        if self.type in ("product", "consu"):
            availability = (
                "https://schema.org/InStock"
                if self.free_qty > 0
                else "https://schema.org/OutOfStock"
            )
            markup_data.setdefault("offers", {})["availability"] = availability
        return markup_data
