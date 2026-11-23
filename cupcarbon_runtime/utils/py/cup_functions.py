# ================================================================
# CupCarbon predefined functions - reference module
# ================================================================
# Import this in your node scripts while editing to get IDE
# auto-completion:
#
#     from cup_functions import *
#
# When the simulation starts, CupCarbon removes this import and
# injects these definitions directly at the top of your script
# (see simulation/CupPythonPreprocessor.java). Keep this file in
# sync with the PRELUDE constant of that class.
# ================================================================
import sys as _cup_sys
import time as _cup_time

def _cup_cmd(*parts):
    print(' '.join(str(p) for p in parts if p is not None), flush=True)

def _cup_ask(*parts):
    _cup_cmd(*parts)
    return _cup_sys.stdin.readline().strip()

def cup_print(*args):
    """Display a message next to the node on the map."""
    _cup_cmd('print', *args)

def cup_mark(node_id=None):
    """Mark this node (or the node with the given id)."""
    _cup_cmd('mark', node_id)

def cup_unmark(node_id=None):
    """Unmark this node (or the node with the given id)."""
    _cup_cmd('unmark', node_id)

def cup_moveto(lon, lat, z=0, node_id=None):
    """Move the node to the given GPS coordinates."""
    if node_id is None:
        _cup_cmd('moveto', lon, lat, z)
    else:
        _cup_cmd('moveto', lon, lat, z, node_id)

cup_move = cup_moveto

def cup_visible(visible=True):
    """Show or hide the node on the map."""
    _cup_cmd('visible', 1 if visible else 0)

def cup_pic(n):
    """Change the icon of the node."""
    _cup_cmd('pic', n)

def cup_image(url='', shape='circle'):
    """Replace the icon of the node by the picture of a URL (PNG, JPEG,
    GIF, BMP), e.g. cup_image('https://randomuser.me/api/portraits/men/7.jpg').
    shape: 'circle' (default, round avatar) or 'square' (whole image).
    The picture is downloaded in the background and cached.
    cup_image() or cup_image('none') restores the built-in icon."""
    if url:
        _cup_cmd('image', url, shape)
    else:
        _cup_cmd('image', 'none')

def cup_speed(ratio, node_id=None):
    """Set the route speed ratio of the node."""
    if node_id is None:
        _cup_cmd('speed', ratio)
    else:
        _cup_cmd('speed', node_id, ratio)

def cup_rudder_angle(angle, node_id=None):
    """Set the route dy (rudder angle) of the node."""
    if node_id is None:
        _cup_cmd('rudder_angle', angle)
    else:
        _cup_cmd('rudder_angle', node_id, angle)

def cup_routewait(seconds):
    """Pause the node on its route for the given duration."""
    _cup_cmd('routewait', seconds)

def cup_routestop(node_id=None):
    """Stop the node on its route."""
    _cup_cmd('routestop', node_id)

def cup_routego(node_id=None):
    """Resume the route of the node."""
    _cup_cmd('routego', node_id)

def cup_route(marker_id1, marker_id2):
    """Generate an OSM route file between two markers."""
    _cup_cmd('route', marker_id1, marker_id2)

def cup_mapcenter(lon, lat):
    """Move the map so that (lon, lat) is at the center of the view (the
    zoom is unchanged). Same order as cup_moveto: longitude first."""
    _cup_cmd('mapcenter', lon, lat)

def cup_drawroutes():
    """Draw all the routes of the project on the map."""
    _cup_cmd('drawroutes')

def cup_alert(*args):
    """Display a short error message in the CupCarbon window."""
    _cup_cmd('alert', *args)

def cup_message(*args):
    """Display a short info message in the CupCarbon window."""
    _cup_cmd('message', *args)

# Broadcast destination: readable aliases for '*' (a bare * is invalid
# Python syntax, so use ALL / BROADCAST — or simply omit the argument).
ALL = '*'
BROADCAST = '*'

def cup_send(message, dest=ALL):
    """Send a message (no spaces) over the RADIO: delivered only to nodes
    inside the radio range of the sender (the message is lost otherwise).

    cup_send('A')            broadcast to the radio neighbors (default)
    cup_send('A', ALL)       same, explicit
    cup_send('A', 3)         to the node 3, only if it is in radio range
    """
    _cup_cmd('send', message, dest)

def cup_fsend(message, dest=ALL):
    """Forced send: like cup_send but IGNORES the radio range (out-of-band
    channel such as a backbone or the Internet). cup_fsend('A', 3) always
    reaches node 3; cup_fsend('A') reaches every node of the project."""
    _cup_cmd('fsend', message, dest)

def cup_read():
    """Read a received message (blocking)."""
    return _cup_ask('read')

def cup_getid():
    """Return the id of the node (int)."""
    return int(_cup_ask('getid'))

def cup_getname():
    """Return the name of the node."""
    return _cup_ask('getname')

def cup_getx():
    """Return the longitude of the node (float)."""
    return float(_cup_ask('getx'))

def cup_gety():
    """Return the latitude of the node (float)."""
    return float(_cup_ask('gety'))

def cup_getxy():
    """Return (longitude, latitude) of the node as floats."""
    x, y = _cup_ask('getxy').split()
    return float(x), float(y)

def cup_ismarked(node_id=None):
    """Return True if the node is marked."""
    return _cup_ask('ismarked', node_id) == '1'

def cup_dsensor():
    """Return True if the sensor unit is detecting something."""
    return _cup_ask('dsensor') == '1'

def cup_getmessage():
    """Return the current displayed message of the node."""
    return _cup_ask('getmessage')

def cup_getaction():
    """Return the action flag of the node."""
    return _cup_ask('getaction') == '1'

def cup_stopsimulation():
    """Stop the whole simulation."""
    _cup_cmd('stopsimulation')

def cup_toagent(txt, chid):
    """Send a text message to the Agentic AI workflows: every CupCarbon
    Read node whose chid parameter matches receives it as output."""
    _cup_cmd('toagent', chid, txt)

def cup_fromagent(chid):
    """Read a message sent by a 'CupCarbon Send' workflow node with the
    given chid (blocking: waits until a message arrives)."""
    return _cup_ask('fromagent', chid)

def cup_wait(seconds):
    """Sleep for the given number of seconds."""
    _cup_time.sleep(seconds)
