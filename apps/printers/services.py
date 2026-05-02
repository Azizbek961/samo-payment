"""
Printer service for receipt printing.
Supports ESC/POS network printers, Windows RAW printing, and Linux CUPS queues.
"""

import os
import shutil
import socket
import subprocess
import tempfile
from datetime import datetime

# Try to import Windows-specific modules
try:
    import win32print
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

ESC = b"\x1b"
GS = b"\x1d"


def esc_init():
    return ESC + b"@"


def esc_align(n):
    return ESC + b"a" + bytes([n])  # 0 left, 1 center


def esc_bold(on):
    return ESC + b"E" + (b"\x01" if on else b"\x00")


def esc_size(big=False):
    return GS + b"!" + (b"\x11" if big else b"\x00")


def esc_cut():
    return GS + b"V" + b"\x00"


def hr():
    return b"--------------------------------\n"


def qr_code(data):
    """Generate QR code ESC/POS commands."""
    data = data.encode("utf-8")

    store_len = len(data) + 3
    pL = store_len % 256
    pH = store_len // 256

    qr = b""
    qr += GS + b"(k" + bytes([4, 0]) + b"1A\x32\x00"
    qr += GS + b"(k" + bytes([3, 0]) + b"1C\x06"
    qr += GS + b"(k" + bytes([3, 0]) + b"1E\x30"
    qr += GS + b"(k" + bytes([pL, pH]) + b"1P0" + data
    qr += GS + b"(k" + bytes([3, 0]) + b"1Q0"

    return qr


def center(text):
    return (text + "\n").encode("utf-8")


def build_receipt(payment, config):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    method_map = {
        "cash": "Naqd",
        "card": "Karta",
        "transfer": "O'tkazma"
    }

    receipt = b""
    receipt += esc_init()

    # ===== HEADER =====
    receipt += esc_align(1)
    receipt += esc_bold(True)
    receipt += esc_size(False)
    receipt += center("SAMO INTERNATIONAL SCHOOL")
    receipt += esc_size(False)
    receipt += esc_bold(False)

    if config.school_address:
        receipt += center(config.school_address)

    if config.school_phone:
        receipt += center("Tel: " + config.school_phone)

    receipt += b"\n"
    receipt += hr()

    # ===== RECEIPT INFO =====
    receipt += esc_align(1)
    receipt += center("TO'LOV CHEKI")
    receipt += hr()

    receipt += center(f"Chek raqami: {payment.receipt_number}")
    receipt += center(f"Sana: {now}")

    receipt += hr()

    # ===== STUDENT =====
    receipt += esc_bold(True)
    receipt += center("O'QUVCHI")
    receipt += esc_bold(False)

    receipt += center(str(payment.student))

    receipt += hr()

    receipt += center(f"To'lov oyi: {payment.month_year.strftime('%Y-%m')}")

    receipt += b"\n"

    # ===== SUMMA =====
    receipt += esc_size(True)
    receipt += esc_bold(True)
    receipt += center(f"{payment.amount} UZS")
    receipt += esc_size(False)
    receipt += esc_bold(False)

    receipt += center(f"To'lov turi: {method_map.get(payment.method)}")

    if payment.notes:
        receipt += b"\n"
        receipt += center("Izoh:")
        receipt += center(payment.notes)

    receipt += hr()

    # ===== QR =====
    receipt += center("Chekni tekshirish")
    qr_data = f"{payment.receipt_number}|{payment.amount}|{payment.student}"
    receipt += qr_code(qr_data)

    receipt += b"\n\n"

    # ===== FOOTER =====
    receipt += center("Rahmat!")
    receipt += center("Yana kutib qolamiz")

    receipt += b"\n\n\n\n\n\n"

    receipt += esc_cut()

    return receipt


def _print_via_windows(receipt, config):
    if not WIN32_AVAILABLE:
        raise RuntimeError("win32print is not available on this system.")

    printer_name = config.printer_name or win32print.GetDefaultPrinter()
    if not printer_name:
        raise RuntimeError("Windows printer name is not configured.")

    handle = win32print.OpenPrinter(printer_name)

    try:
        win32print.StartDocPrinter(handle, 1, ("Receipt", None, "RAW"))
        win32print.StartPagePrinter(handle)

        win32print.WritePrinter(handle, receipt)

        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)

    finally:
        win32print.ClosePrinter(handle)

    return True


def _print_via_network(receipt, config):
    if not config.ip_address:
        raise RuntimeError("Network printer IP address is not configured.")

    with socket.create_connection((config.ip_address, config.port), timeout=10) as conn:
        conn.sendall(receipt)

    return True


def _print_via_linux(receipt, config):
    if not config.printer_name:
        raise RuntimeError("Linux CUPS printer queue name is not configured.")

    print_command = shutil.which("lp") or shutil.which("lpr")
    if not print_command:
        raise RuntimeError("CUPS print command not found. Install `cups-client` on the Linux server.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as temp_file:
            temp_file.write(receipt)
            temp_path = temp_file.name

        if os.path.basename(print_command) == "lp":
            command = [print_command, "-d", config.printer_name, "-o", "raw", temp_path]
        else:
            command = [print_command, "-P", config.printer_name, "-o", "raw", temp_path]

        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip() or "Unknown print error"
            raise RuntimeError(error_output)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

    return True


def print_receipt(payment, config):
    """
    Print a receipt to the configured printer.

    Args:
        payment: Payment object
        config: PrinterConfig object

    Returns:
        bool: True if printing succeeded
    """
    receipt = build_receipt(payment, config)

    if config.printer_type == "network":
        return _print_via_network(receipt, config)
    if config.printer_type == "linux":
        return _print_via_linux(receipt, config)
    if config.printer_type == "windows":
        return _print_via_windows(receipt, config)

    raise RuntimeError(f"Unsupported printer type: {config.printer_type}")
