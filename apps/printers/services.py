from datetime import datetime
import os

# Windows-only import
WIN32_AVAILABLE = False
win32print = None

if os.name == "nt":  # Windows
    try:
        import win32print  # type: ignore
        WIN32_AVAILABLE = True
    except Exception:
        WIN32_AVAILABLE = False


ESC = b"\x1b"
GS = b"\x1d"

def esc_init():
    return ESC + b"@"

def esc_align(n: int):
    return ESC + b"a" + bytes([n])  # 0 left, 1 center, 2 right

def esc_bold(on: bool):
    return ESC + b"E" + (b"\x01" if on else b"\x00")

def esc_size(double_wh: bool = False):
    return GS + b"!" + (b"\x11" if double_wh else b"\x00")

def esc_cut():
    return GS + b"V" + b"\x00"

def hr(width_chars=32):
    return ("-" * width_chars + "\n").encode("utf-8")

def pad_lr(left: str, right: str, width=32):
    space = width - len(left) - len(right)
    if space < 1:
        return (left + " " + right + "\n").encode("utf-8")
    return (left + (" " * space) + right + "\n").encode("utf-8")

def escpos_qr(data: str, size: int = 6, ec_level: int = 48):
    """
    ESC/POS QR (Model 2).
    size: 1..16
    ec_level: 48(L),49(M),50(Q),51(H)
    """
    bdata = data.encode("utf-8")
    store_len = len(bdata) + 3
    pL = store_len & 0xFF
    pH = (store_len >> 8) & 0xFF

    cmd = b""
    cmd += GS + b"(k" + bytes([4, 0]) + b"1A" + bytes([50, 0])                       # model 2
    cmd += GS + b"(k" + bytes([3, 0]) + b"1C" + bytes([max(1, min(size, 16))])        # size
    cmd += GS + b"(k" + bytes([3, 0]) + b"1E" + bytes([ec_level])                      # EC level
    cmd += GS + b"(k" + bytes([pL, pH]) + b"1P0" + bdata                               # store
    cmd += GS + b"(k" + bytes([3, 0]) + b"1Q0"                                         # print
    return cmd

def print_receipt(payment, config):
    """
    Windows serverda: chek chiqaradi.
    Fly.io (Linux)da: win32print yo'qligi uchun exception tashlamaydi, False qaytaradi.
    """

    # Printer type tekshiruv (sizdagi eski shart)
    if config.printer_type != "windows":
        # Oldin raise qilgansiz. Fly'da yiqitmaslik uchun False qaytaramiz.
        return False

    # Agar platforma Windows bo'lmasa yoki win32print import bo'lmasa:
    if not WIN32_AVAILABLE:
        return False

    printer_name = config.printer_name or "POSPrinter POS80"
    WIDTH = 32

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    receipt = b""
    receipt += esc_init()

    # HEADER
    receipt += esc_align(1)
    receipt += esc_bold(True)
    receipt += esc_size(True)
    receipt += ("Samo International Schol\n").encode("utf-8")
    receipt += esc_size(False)
    receipt += esc_bold(False)

    if config.school_address:
        receipt += (config.school_address + "\n").encode("utf-8")
    if config.school_phone:
        receipt += ("Tel: " + config.school_phone + "\n").encode("utf-8")

    receipt += b"\n" + hr(WIDTH)

    # INFO
    receipt += esc_align(0)
    receipt += pad_lr("Chek No:", str(payment.receipt_number), WIDTH)
    receipt += pad_lr("Sana:", now_str, WIDTH)
    receipt += hr(WIDTH)

    # STUDENT
    receipt += esc_bold(True) + ("O'quvchi:\n").encode("utf-8") + esc_bold(False)
    receipt += (f"{payment.student}\n").encode("utf-8")

    receipt += hr(WIDTH)
    receipt += pad_lr("To'lov oyi:", payment.month_year.strftime("%Y-%m"), WIDTH)

    receipt += hr(WIDTH)
    receipt += esc_bold(True)
    receipt += pad_lr("SUMMA:", f"{payment.amount} UZS", WIDTH)
    receipt += esc_bold(False)

    method_map = {"cash": "Naqd", "card": "Karta", "transfer": "O‘tkazma"}
    receipt += pad_lr("To'lov turi:", method_map.get(payment.method, payment.method), WIDTH)

    if payment.notes:
        receipt += hr(WIDTH)
        receipt += ("Izoh:\n").encode("utf-8")
        receipt += (payment.notes.strip() + "\n").encode("utf-8")

    # QR (CENTER)
    receipt += hr(WIDTH)
    receipt += esc_align(1)
    receipt += ("QR orqali tekshirish:\n").encode("utf-8")

    qr_data = f"RCPT={payment.receipt_number}|STUDENT={payment.student}|AMOUNT={payment.amount}|DATE={now_str}"
    receipt += escpos_qr(qr_data, size=6, ec_level=48)
    receipt += b"\n"

    # FOOTER
    receipt += ("Rahmat!\n").encode("utf-8")
    receipt += ("Yana kutib qolamiz.\n").encode("utf-8")

    receipt += b"\n\n\n\n\n\n\n\n\n\n"
    receipt += esc_cut()

    # SEND
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        win32print.StartDocPrinter(hPrinter, 1, ("Receipt", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, receipt)
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)

    return True