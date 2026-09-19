"""Validate passive snapshots from reload_browser.py. Never drives game state."""
from copy import deepcopy
from math import isfinite


def _presentation_errors(state):
    errors=[]
    for key in ('frame','time','remaining','shots','charge','completed'):
        value=state.get(key)
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not isfinite(value):
            errors.append('invalid '+key)
    if state.get('inputs') or state.get('trigger') or state.get('aiming') or state.get('charge') != 0:
        errors.append('cancelled input or charge is active')
    if state.get('glError') != 0: errors.append('WebGL error')
    rendered=state.get('rendered') or {}
    if rendered.get('selected') != state.get('selected'): errors.append('stale rendered equipment')
    instances=rendered.get('instances')
    if not isinstance(instances,dict) or not instances or any(v != 1 for v in instances.values()):
        errors.append('missing or duplicated equipment part')
    return errors


def pause_errors(before,after):
    """Both observations are taken inside the selector, with real RAF running."""
    errors=_presentation_errors(before)+_presentation_errors(after)
    if before['mode']!='arsenal' or after['mode']!='arsenal' or not before['frozen'] or not after['frozen']:
        errors.append('selector did not preserve its frozen presentation')
    if not after['frame']>before['frame']: errors.append('browser loop did not advance')
    for key in ('time','remaining','reloadId','selected','ammo','shots','completed','rendered'):
        if after[key]!=before[key]: errors.append(key+' changed during pause')
    return errors


def completion_errors(before,after,capacity,selected=None):
    """Check a completed reload, or a cancelled reload after switching equipment."""
    errors=_presentation_errors(after)
    switching=selected is not None
    wanted=selected if switching else before['selected']
    if after['mode'] not in ('play','pause') or after['frozen'] or after['selected']!=wanted:
        errors.append('incorrect return mode, frozen presentation or selection')
    if not after['frame']>before['frame'] or not after['time']>=before['time']+before['remaining']-1e-8:
        errors.append('completion was not observed across a running simulation')
    if after['remaining']!=0 or after['reloadId'] is not None: errors.append('reload is still pending')
    expected=deepcopy(before['ammo'])
    if not switching:
        ammo=expected[before['selected']]
        transfer=min(capacity-ammo['loaded'],ammo['reserve'])
        ammo['loaded']+=transfer;ammo['reserve']-=transfer
    if after['ammo']!=expected: errors.append('incorrect ammunition transfer')
    if after['shots']!=before['shots']: errors.append('phantom shot')
    if after['completed']!=before['completed']+(0 if switching else 1):
        errors.append('reload completion was missing or duplicated')
    magazine=after['rendered'].get('magazine') or {}
    if magazine.get('attachedToHand') is not False or magazine.get('offset')!=[0,0,0] or magazine.get('rotation')!=[0,0,0]:
        errors.append('detached reload piece survived completion or cancellation')
    return errors
