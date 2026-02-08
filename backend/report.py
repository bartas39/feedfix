# backend/report.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from datetime import datetime
import os


# Ścieżka do fontu UTF-8
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FONT_PATH = os.path.join(
    BASE_DIR,
    "fonts",
    "NotoSans-Regular.ttf"
)

# Rejestracja fontu
pdfmetrics.registerFont(TTFont("Noto", FONT_PATH))


def safe(val):
    if val:
        return str(val)
    return "brak danych"


def generate_pdf_report(data: dict, filename: str):

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    margin = 50
    y = height - 60

    # Domyślny font
    c.setFont("Noto", 12)

    # ---------------- NAGŁÓWEK ----------------

    c.setFont("Noto", 24)
    c.drawString(margin, y, "Raport jakości FeedFix")
    y -= 30

    c.setFont("Noto", 11)
    c.drawString(
        margin,
        y,
        f"Data wygenerowania: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    y -= 35

    # ---------------- WYNIK ----------------

    score = data.get("score", 0)

    c.setFont("Noto", 18)
    c.drawString(margin, y, f"Wynik jakości: {score} / 100")
    y -= 25

    # ---------------- PODSUMOWANIE ----------------

    c.setFont("Noto", 15)
    c.drawString(margin, y, "Podsumowanie")
    y -= 22

    c.setFont("Noto", 12)

    c.drawString(margin, y, f"Liczba produktów: {data.get('products_checked', 0)}")
    y -= 16

    c.drawString(margin, y, f"Błędy krytyczne: {data.get('total_critical', 0)}")
    y -= 16

    c.drawString(margin, y, f"Ostrzeżenia: {data.get('total_warnings', 0)}")
    y -= 30

    # ---------------- STATYSTYKI ----------------

    c.setFont("Noto", 15)
    c.drawString(margin, y, "Najczęstsze problemy")
    y -= 22

    c.setFont("Noto", 12)

    stats = data.get("error_stats", {})

    if not stats:
        c.drawString(margin, y, "Nie wykryto istotnych problemów.")
        y -= 16

    for key, count in sorted(stats.items(), key=lambda x: -x[1]):

        name = key.replace("_", " ")

        c.drawString(
            margin,
            y,
            f"- Pole: {name} → {count} produktów"
        )

        y -= 16

        if y < 120:
            c.showPage()
            c.setFont("Noto", 12)
            y = height - 60

    y -= 25

    # ---------------- BŁĘDY ----------------

    c.setFont("Noto", 15)
    c.drawString(margin, y, "Lista błędów krytycznych")
    y -= 22

    c.setFont("Noto", 11)

    critical = data.get("critical_errors", [])[:30]

    if not critical:
        c.drawString(margin, y, "Brak błędów krytycznych.")
        y -= 15

    for err in critical:

        title = safe(err.get("title"))
        pid = safe(err.get("product_id"))
        field = safe(err.get("field"))
        link = safe(err.get("link"))

        c.drawString(margin, y, f"Produkt: {title}")
        y -= 13

        c.drawString(margin + 15, y, f"ID: {pid}")
        y -= 13

        c.drawString(margin + 15, y, f"Brakuje: {field}")
        y -= 13

        c.drawString(margin + 15, y, f"Link: {link}")
        y -= 16

        if y < 120:
            c.showPage()
            c.setFont("Noto", 11)
            y = height - 60

    y -= 20

    # ---------------- PLAN ----------------

    c.setFont("Noto", 15)
    c.drawString(margin, y, "Plan naprawczy")
    y -= 22

    c.setFont("Noto", 12)

    steps = [
        "☐ Uzupełnij brakujące dane produktów",
        "☐ Popraw format cen",
        "☐ Zweryfikuj dostępność",
        "☐ Uzupełnij opisy",
        "☐ Przetestuj feed ponownie"
    ]

    for step in steps:
        c.drawString(margin, y, step)
        y -= 16

    y -= 25

    # ---------------- STOPKA ----------------

    c.setFont("Noto", 10)

    c.drawString(
        margin,
        y,
        "FeedFix – profesjonalna analiza feedów produktowych"
    )

    c.save()
