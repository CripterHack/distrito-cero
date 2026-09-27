"""Disjoint scheduling of the existing sight producer, never new game scenarios."""

SIGHT_PARTITIONS = (('base', 40), ('cross-family', 18))
SWITCH_CASES = (
    ('pistol', 'revolver', None), ('revolver', 'pistol', None),
    ('pistol', 'revolver', .46), ('revolver', 'pistol', .46),
    ('rifle', 'pistol', None), ('pistol', 'rifle', None),
    ('rifle', 'pistol', .46), ('pistol', 'rifle', .46),
)


def sight_cases(partition: str) -> tuple:
    """Keep both directions and reload cases; reject unknown partitions."""
    if partition == 'all':
        return SWITCH_CASES
    if partition == 'base':
        return SWITCH_CASES[:4]
    if partition == 'cross-family':
        return SWITCH_CASES[4:]
    raise ValueError('Unknown sight partition: ' + str(partition))
