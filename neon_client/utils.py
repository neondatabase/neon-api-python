def compact_mapping(obj):
    """Compact a mapping by removing None values."""

    return {k: v for k, v in obj.items() if v is not None}
