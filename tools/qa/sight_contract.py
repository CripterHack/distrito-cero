"""Disjoint scheduling of the canonical sight producer and measured exchange cases."""

SIGHT_PARTITIONS = (('base', 40), ('cross-family', 26), ('revolver-reload', 28))
SWITCH_CASES = (
    ('pistol', 'revolver', None), ('revolver', 'pistol', None),
    ('pistol', 'revolver', .46), ('revolver', 'pistol', .46),
    ('rifle', 'pistol', None), ('pistol', 'rifle', None),
    ('rifle', 'pistol', .46), ('pistol', 'rifle', .46),
    ('rifle', 'revolver', None), ('revolver', 'rifle', None),
    ('rifle', 'revolver', .46), ('revolver', 'rifle', .46),
    ('smg', 'revolver', None), ('revolver', 'smg', None),
    ('smg', 'revolver', .46), ('revolver', 'smg', .46),
)


def sight_cases(partition: str) -> tuple:
    """Keep both directions and reload cases; reject unknown partitions."""
    if partition == 'all':
        return SWITCH_CASES
    if partition == 'base':
        return SWITCH_CASES[:4]
    if partition == 'cross-family':
        return SWITCH_CASES[4:10]
    # Keep the historical scheduling key; its spare budget also covers measured SMG exchanges.
    if partition == 'revolver-reload':
        return SWITCH_CASES[10:]
    raise ValueError('Unknown sight partition: ' + str(partition))
