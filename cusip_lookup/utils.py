def deduplicate_list(_list):
    """
    Deduplicate input but preserve order.
    """
    seen = set()
    seen_add = seen.add
    return [
        x for x in _list
        if not (x in seen or seen_add(x))
    ]
