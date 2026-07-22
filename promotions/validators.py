def normalize_promotion_code(value):
    if not value:
        return ""

    return value.strip().upper()