from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from apps.printers.services import build_receipt, print_receipt


class PrinterServiceTests(SimpleTestCase):
    def _payment(self):
        return SimpleNamespace(
            receipt_number="RCPT-20260421-0001",
            student=SimpleNamespace(full_name="Ali Valiyev", __str__=lambda self: self.full_name),
            amount=250000,
            month_year=SimpleNamespace(strftime=lambda fmt: "2026-04"),
            method="cash",
            notes="Sinov to'lovi",
        )

    def _config(self, printer_type="network", **overrides):
        data = {
            "printer_type": printer_type,
            "ip_address": "192.168.1.50",
            "port": 9100,
            "printer_name": "POS80",
            "school_address": "Tashkent",
            "school_phone": "+998901234567",
        }
        data.update(overrides)
        return SimpleNamespace(**data)

    def test_build_receipt_contains_basic_data(self):
        receipt = build_receipt(self._payment(), self._config())

        self.assertIn(b"TO'LOV CHEKI", receipt)
        self.assertIn(b"RCPT-20260421-0001", receipt)
        self.assertIn(b"250000 UZS", receipt)

    @patch("apps.printers.services._print_via_network")
    def test_print_receipt_uses_network_transport(self, network_print):
        network_print.return_value = True

        result = print_receipt(self._payment(), self._config(printer_type="network"))

        self.assertTrue(result)
        network_print.assert_called_once()

    @patch("apps.printers.services._print_via_linux")
    def test_print_receipt_uses_linux_transport(self, linux_print):
        linux_print.return_value = True

        result = print_receipt(self._payment(), self._config(printer_type="linux"))

        self.assertTrue(result)
        linux_print.assert_called_once()

    @patch("apps.printers.services.socket.create_connection")
    def test_network_transport_sends_receipt_bytes(self, create_connection):
        connection = MagicMock()
        create_connection.return_value.__enter__.return_value = connection

        result = print_receipt(self._payment(), self._config(printer_type="network"))

        self.assertTrue(result)
        connection.sendall.assert_called_once()
