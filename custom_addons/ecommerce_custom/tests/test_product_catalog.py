from odoo.tests.common import SavepointCase


class TestProductCatalog(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.template"].create({
            "name": "Catalog test product",
            "is_featured": True,
            "is_promotional": True,
            "promotion_label": "Test offer",
        })

    def test_homepage_merchandising_fields(self):
        self.assertTrue(self.product.is_featured)
        self.assertTrue(self.product.is_promotional)
        self.assertEqual(self.product.promotion_label, "Test offer")

    def test_native_order_model_remains_source_of_truth(self):
        self.assertEqual(self.env["sale.order"]._name, "sale.order")
        self.assertEqual(self.env["sale.order.line"]._name, "sale.order.line")
