def parse_callback_data(raw: str) -> dict:
    """
    Парсит строки формата ключ=значение с разделителем ;
    """
    params = {}
    for part in raw.split(";"):
        if "=" in part:
            key, val = part.split("=", 1)
            params[key] = val
    return params