# backend/validator/google.py


REQUIRED_FIELDS = [
    "id",
    "title",
    "description",
    "link",
    "image_link",
    "price",
    "availability"
]

CRITICAL_FIELDS = [
    "id",
    "link",
    "price",
    "availability"
]


def get_text(item, field, ns):

    el = item.find(f"g:{field}", ns)

    if el is not None and el.text:
        return el.text.strip()

    return None


def validate_google_feed(root):

    ns = {"g": "http://base.google.com/ns/1.0"}

    items = root.findall(".//item")

    critical_errors = []
    warnings = []

    error_stats = {}

    total_fields = len(items) * len(REQUIRED_FIELDS)
    missing_fields = 0

    for i, item in enumerate(items, start=1):

        product_id = get_text(item, "id", ns)
        title = get_text(item, "title", ns)
        link = get_text(item, "link", ns)

        # Braki wymaganych pól
        for field in REQUIRED_FIELDS:

            val = get_text(item, field, ns)

            if not val:

                missing_fields += 1

                if field in CRITICAL_FIELDS:
                    severity = "critical"
                else:
                    severity = "warning"

                # Statystyki
                error_stats[field] = error_stats.get(field, 0) + 1

                error_obj = {
                    "index": i,
                    "product_id": product_id,
                    "title": title,
                    "link": link,
                    "field": field,
                    "severity": severity,
                    "error": "Brak wymaganego pola"
                }

                if severity == "critical":
                    critical_errors.append(error_obj)
                else:
                    warnings.append(error_obj)

        # Walidacja ceny
        price = get_text(item, "price", ns)

        if price and " " not in price:

            error_stats["price_format"] = error_stats.get("price_format", 0) + 1

            warnings.append({
                "index": i,
                "product_id": product_id,
                "title": title,
                "link": link,
                "field": "price",
                "severity": "warning",
                "error": "Niepoprawny format ceny (np. 99.99 PLN)"
            })

    # Score
    score = 100

    if total_fields > 0:
        penalty = (missing_fields / total_fields) * 100
        score = max(0, round(100 - penalty))

    return {
        "products_checked": len(items),
        "score": score,

        "critical_errors": critical_errors,
        "warnings": warnings,

        "total_critical": len(critical_errors),
        "total_warnings": len(warnings),

        "error_stats": error_stats
    }
