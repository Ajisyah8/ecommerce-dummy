from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _check_website_cart_stock(self):
        """Recheck physical stock immediately before payment/confirmation."""
        for order in self:
            for line in order.website_order_line.filtered(
                lambda item: item.product_id and not item.is_delivery
            ):
                product = line.product_id
                if product.type not in ("product", "consu"):
                    continue

                stock_product = product.with_context(warehouse_id=order.warehouse_id.id)
                requested_qty = line.product_uom_id._compute_quantity(
                    line.product_uom_qty, product.uom_id
                )
                available_qty = max(stock_product.free_qty, 0.0)
                if float_compare(
                    requested_qty,
                    available_qty,
                    precision_rounding=product.uom_id.rounding,
                ) > 0:
                    raise ValidationError(_(
                        "The product %(product)s no longer has enough stock. "
                        "Requested: %(requested)s %(unit)s; available: %(available)s %(unit)s.",
                        product=product.display_name,
                        requested=requested_qty,
                        available=available_qty,
                        unit=product.uom_id.name,
                    ))

    def _verify_updated_quantity(self, order_line, product_id, new_qty, uom_id, **kwargs):
        """Prevent the public cart from exceeding immediately available stock.

        Native sale orders remain the source of truth. This hook only constrains
        website cart mutations and deliberately leaves services and products
        without stock management untouched.
        """
        quantity, warning = super()._verify_updated_quantity(
            order_line, product_id, new_qty, uom_id, **kwargs
        )
        if quantity <= 0 or not self:
            return quantity, warning

        product = self.env["product.product"].browse(product_id).exists()
        if not product or product.type not in ("product", "consu"):
            return quantity, warning

        order = self[:1]
        stock_product = product.with_context(warehouse_id=order.warehouse_id.id)
        available_qty = max(stock_product.free_qty, 0.0)
        requested_uom = self.env["uom.uom"].browse(uom_id).exists() or product.uom_id
        requested_product_qty = requested_uom._compute_quantity(quantity, product.uom_id)

        existing_product_qty = 0.0
        if order_line:
            existing_product_qty = order_line.product_uom_id._compute_quantity(
                order_line.product_uom_qty, product.uom_id
            )
        maximum_product_qty = available_qty + existing_product_qty

        if float_compare(
            requested_product_qty,
            maximum_product_qty,
            precision_rounding=product.uom_id.rounding,
        ) <= 0:
            return quantity, warning

        capped_quantity = product.uom_id._compute_quantity(
            maximum_product_qty, requested_uom, rounding_method="DOWN"
        )
        stock_warning = _(
            "Only %(available)s %(unit)s of %(product)s are currently available. "
            "The cart quantity was adjusted.",
            available=available_qty,
            unit=product.uom_id.name,
            product=product.display_name,
        )
        return max(capped_quantity, 0.0), stock_warning

    def _check_cart_is_ready_to_be_paid(self):
        result = super()._check_cart_is_ready_to_be_paid()
        self._check_website_cart_stock()
        return result

    def action_confirm(self):
        website_orders = self.filtered(lambda order: order.website_id)
        website_orders._check_website_cart_stock()
        return super().action_confirm()
