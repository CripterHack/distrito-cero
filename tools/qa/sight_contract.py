"""Disjoint scheduling of the canonical sight producer and measured exchange cases."""

SIGHT_PARTITIONS = (('base', 56), ('cross-family', 44), ('revolver-reload', 48))
SWITCH_CASES = (
    ('pistol', 'revolver', None), ('revolver', 'pistol', None),
    ('pistol', 'revolver', .46), ('revolver', 'pistol', .46),
    ('rifle', 'pistol', None), ('pistol', 'rifle', None),
    ('rifle', 'pistol', .46), ('pistol', 'rifle', .46),
    ('rifle', 'revolver', None), ('revolver', 'rifle', None),
    ('rifle', 'revolver', .46), ('revolver', 'rifle', .46),
    ('smg', 'revolver', None), ('revolver', 'smg', None),
    ('smg', 'revolver', .46), ('revolver', 'smg', .46),
    ('pistol', 'smg', None), ('smg', 'pistol', None),
    ('pistol', 'smg', .46), ('smg', 'pistol', .46),
    ('pistol', 'shotgun', None), ('shotgun', 'pistol', None),
    ('pistol', 'shotgun', .46), ('shotgun', 'pistol', .46),
    ('shotgun', 'revolver', None), ('revolver', 'shotgun', None),
    ('shotgun', 'revolver', .46), ('revolver', 'shotgun', .46),
)


# The producer and acceptance gate share these labels. Base counts them inside
# checks; the remaining partitions report them separately without inflating QA.
SIGHT_GUARDS = {
    'maps': 'Embedded skin maps decode in the production renderer',
    'selector': 'Translucent selector remains paused and blocks game actions',
    'inputs': 'Closing selection does not restore a trigger or aiming request',
    'storage': 'Visual inspection never overwrites the saved catalogue',
    'runtime': 'No JavaScript or graphics exceptions or external requests',
}


def validate_sight_report(report: dict, partition: str) -> None:
    """Reject diagnostic, incomplete or mislabelled sight evidence, without retries."""
    expected = dict(SIGHT_PARTITIONS).get(partition)
    if expected is None:
        raise ValueError('Unknown sight partition: ' + str(partition))
    if report.get('partition') != partition:
        raise ValueError('Sight report belongs to a different partition.')
    if report.get('comparisonOnly') is not False:
        raise ValueError('Sight acceptance requires explicit non-comparison mode.')
    checks = report.get('checks')
    if not isinstance(checks, list) or len(checks) != expected:
        raise ValueError('Unexpected number of sight checks.')
    names = []
    for check in checks:
        if not isinstance(check, dict) or check.get('pass') is not True:
            raise ValueError('A sight check did not pass.')
        name = check.get('name')
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Sight checks require non-empty names.')
        names.append(name)
    if len(set(names)) != len(names):
        raise ValueError('Duplicate sight check names.')
    required = set(SIGHT_GUARDS.values())
    guards = report.get('guards')
    if partition == 'base':
        if guards != [] or not required.issubset(names):
            raise ValueError('Base sight guards must occur once inside checks.')
        return
    if not isinstance(guards, list) or len(guards) != len(required):
        raise ValueError('Sight requires all five separate guards.')
    guard_names = []
    for guard in guards:
        if not isinstance(guard, dict) or guard.get('pass') is not True:
            raise ValueError('A sight guard did not pass.')
        name = guard.get('name')
        if not isinstance(name, str):
            raise ValueError('Sight guards require names.')
        guard_names.append(name)
    if set(guard_names) != required:
        raise ValueError('Missing, duplicate or unknown sight guard names.')


def sight_cases(partition: str) -> tuple:
    """Keep both directions and reload cases; reject unknown partitions."""
    if partition == 'all':
        return SWITCH_CASES
    if partition == 'base':
        return SWITCH_CASES[:4] + SWITCH_CASES[16:18] + SWITCH_CASES[20:22]
    if partition == 'cross-family':
        return SWITCH_CASES[4:10] + SWITCH_CASES[18:19] + SWITCH_CASES[22:23] + SWITCH_CASES[24:26]
    # Preserve existing per-partition order; distribute the four new cases
    # over existing runners without removing checks or raising their limits.
    # Keep base unchanged; append free cases to cross-family and reload exits here.
    if partition == 'revolver-reload':
        return SWITCH_CASES[10:16] + SWITCH_CASES[19:20] + SWITCH_CASES[23:24] + SWITCH_CASES[26:]
    raise ValueError('Unknown sight partition: ' + str(partition))
