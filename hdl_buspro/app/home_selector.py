def select_homes(all_homes, required_names):
    if not required_names:
        raise RuntimeError(
            "HDL_HOME_NAMES is empty. You must explicitly specify one or more HDL object names."
        )

    selected = []
    missing = []

    for name in required_names:
        found = next((h for h in all_homes if h.get("homeName") == name), None)
        if found:
            selected.append(found)
        else:
            missing.append(name)

    if missing:
        available = [h.get("homeName", "") for h in all_homes]
        raise RuntimeError(
            f"HDL homes not found: {missing}. Available homes: {available}"
        )

    return selected