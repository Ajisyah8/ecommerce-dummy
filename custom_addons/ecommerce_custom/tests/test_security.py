from odoo.tests.common import SavepointCase


class TestCustomerOrderSecurity(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_group = cls.env.ref("base.group_portal")
        cls.partner_a = cls.env["res.partner"].create({"name": "Portal Customer A"})
        cls.partner_b = cls.env["res.partner"].create({"name": "Portal Customer B"})
        cls.portal_user = cls.env["res.users"].with_context(
            no_reset_password=True
        ).create({
            "name": "Portal User A",
            "login": "portal-user-a@example.test",
            "partner_id": cls.partner_a.id,
            "groups_id": [(6, 0, [cls.portal_group.id])],
        })
        cls.order_a = cls.env["sale.order"].create({
            "partner_id": cls.partner_a.id,
        })
        cls.order_b = cls.env["sale.order"].create({
            "partner_id": cls.partner_b.id,
        })

    def test_portal_user_only_reads_own_customer_orders(self):
        orders = self.env["sale.order"].with_user(self.portal_user).search([])
        self.assertIn(self.order_a, orders)
        self.assertNotIn(self.order_b, orders)

    def test_native_portal_rule_is_partner_scoped(self):
        order_rule = self.env.ref("sale.sale_order_rule_portal")
        line_rule = self.env.ref("sale.sale_order_line_rule_portal")
        self.assertIn("commercial_partner_id", order_rule.domain_force)
        self.assertIn("commercial_partner_id", line_rule.domain_force)
