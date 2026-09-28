from odoo.tests.common import SavepointCase


class TestPaymentArchitecture(SavepointCase):
    def test_native_wire_transfer_provider_is_available(self):
        provider = self.env["payment.provider"].search([
            ("code", "=", "custom"),
            ("custom_mode", "=", "wire_transfer"),
        ], limit=1)
        self.assertTrue(provider, "Native Community wire transfer provider is unavailable")
        self.assertEqual(provider.custom_mode, "wire_transfer")
