

def build_where_clause(and_keywords, or_keywords, not_keywords, sources):
    conditions = []
    params = []

    for kw in and_keywords:
        if kw:
            conditions.append("LOWER(title) LIKE %s")
            params.append(f"%{kw.lower()}%")

    if or_keywords:
        or_conditions = []
        for kw in or_keywords:
            if kw:
                or_conditions.append("LOWER(title) LIKE %s")
                params.append(f"%{kw.lower()}%")
        if or_conditions:
            conditions.append(f"({' OR '.join(or_conditions)})")

    for kw in not_keywords:
        if kw:
            conditions.append("LOWER(title) NOT LIKE %s")
            params.append(f"%{kw.lower()}%")

    if sources:
        filter_sources = sources[1:] if len(sources) > 1 else sources
        placeholders = ",".join(["%s"] * len(filter_sources))
        conditions.append(f"source_name IN ({placeholders})")
        params.extend(filter_sources)

    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    return where_clause, params