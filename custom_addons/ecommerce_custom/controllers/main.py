from odoo import http
from odoo.http import request


class EcommerceHome(http.Controller):
    @http.route(
        ["/", "/ecommerce/home"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
        readonly=True,
    )
    def ecommerce_home(self, **kwargs):
        ProductTemplate = request.env["product.template"]
        product_domain = [
            ("sale_ok", "=", True),
            ("is_published", "=", True),
        ]
        featured_products = ProductTemplate.search(
            product_domain + [("is_featured", "=", True)],
            order="website_sequence, id desc",
            limit=8,
        )
        promotional_products = ProductTemplate.search(
            product_domain + [("is_promotional", "=", True)],
            order="website_sequence, id desc",
            limit=4,
        )
        new_products = ProductTemplate.search(
            product_domain,
            order="publish_date desc, id desc",
            limit=8,
        )
        categories = request.env["product.public.category"].search(
            [("parent_id", "=", False)],
            order="sequence, name, id",
            limit=8,
        )
        return request.render(
            "ecommerce_custom.homepage",
            {
                "featured_products": featured_products,
                "promotional_products": promotional_products,
                "new_products": new_products,
                "ecommerce_categories": categories,
            },
        )
