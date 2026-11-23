---
name: cupcarbon-coding
description: Write Python scripts for CupCarbon IoT nodes using the cup_* API. Use when the user asks for CupCarbon node code, cup_ functions, IoT node scripts, WSN/Smart City simulation behaviors (mark, move, routes, messages, sensors, MQTT alerts, agentic workflows bridge) for the CupCarbon simulator.
---

# CupCarbon IoT node coding (cup_* API)

CupCarbon (cupcarbon.com) is a Smart City / IoT / WSN simulator. Each IoT
node runs a real external Python 3 script. Scripts MUST start with:

```python
from cup_functions import *
```

(gives IDE completion; CupCarbon injects the real implementations at
simulation start). One script file can be assigned to many nodes; each node
runs its own process. Save files in the project's `scripts/` folder with the
`.py` extension and assign them in Device Parameters (or with the console
command `set script <id> <file.py>`).

## Rules
- Coordinates are WGS84: longitude, latitude (in this order for cup_moveto).
  ~0.001 degrees of latitude = 111 m; longitude degrees shrink by
  cos(latitude).
- Use `cup_wait(seconds)` for delays (simulated-time aware). Never
  `time.sleep` for simulation timing. Keep a small `cup_wait` in every loop.
- `cup_print` accepts several args: `cup_print("T:", 25.4)`.
- Long-running behaviors are `while True:` loops.
- A project is either IoT (these scripts) or WSN (SenScript) — never both.
- External libraries are allowed (real Python): e.g. `paho-mqtt` for MQTT
  (`pip install paho-mqtt`). Run MQTT callbacks in paho's own thread and
  pass data to the main loop through a `queue.Queue`.
- Give each MQTT client a unique client_id (append `cup_getid()`).

## API reference (33 functions)

Display / appearance:
- `cup_print(*args)` — message next to the node on the map
- `cup_mark(node_id=None)` / `cup_unmark(node_id=None)` — highlight on/off
  (own node when node_id omitted)
- `cup_visible(True|False)` — show/hide the node
- `cup_pic(n)` — change the node icon (integer index)
  Icon numbers: 0 Light/LED, 1 Switch, 2 Microcontroller, 3 AI-GPU, 4 Spot, 5 Smartphone, 6 Person, 7 Motherboard, 8 Server, 9 Cloud, 10 Big-Data Server, 11 Ship, 12 Aircraft, 13 Drone, 14 Car, 15 Arm, 16 EV Station, 17 Light Spot, 18 Worker, 19 Conveyor Belt, 20 Shimmer Sensor, 21 Monitor, 22 Industrial Control Unit, 23 Camera, 24 Base Station, 25 Industrial Dashboard, 26 Gray Car Top View, 27 Parking (Top View), 28 Parking Sign, 29 Fire Truck, 30 ESP32 Board, 31 Digital Twin, 32 Red Car Top View, 33 Green Car Top View, 34 Yellow/Gold Car Top View, 35 Orange Car Top View, 36 White Car Top View, 37 Barrier, 38 Gas Sensor, 39 Distance Sensor, 40 Light Sensor, 41 Water Sensor, 42 Big Building, 43 Fire, 44 Person Icon, 45 Dog Robot, 46 Ambulance.
- `cup_image(url='', shape='circle')` — picture from a URL (PNG/JPEG/GIF/BMP)
  as the node icon, downloaded in the background and cached; 'circle' =
  round avatar, 'square' = whole image; `cup_image()` restores the icon.
  Example: `cup_image('https://randomuser.me/api/portraits/men/7.jpg')`
- `cup_alert(*args)` / `cup_message(*args)` — short error / info message in
  the CupCarbon window

Reading (return typed values):
- `cup_getid() -> int`, `cup_getname() -> str`
- `cup_getx() -> float` (longitude), `cup_gety() -> float` (latitude),
  `cup_getxy() -> (lon, lat)`
- `cup_ismarked(node_id=None) -> bool`
- `cup_dsensor() -> bool` — True if the sensing unit detects an event
  (gas, fire, mobile in range)
- `cup_getmessage() -> str` — current displayed message
- `cup_getaction() -> str` — last user action on the node

Mobility:
- `cup_moveto(lon, lat, z=0, node_id=None)` — jump to GPS position
- `cup_route(node_id1, node_id2)` — computes a real ROAD route from node 1
  to node 2 (web routing API, needs internet) and assigns it to node 1
- `cup_routego(node_id=None)` / `cup_routestop(node_id=None)` — start/stop
  following the assigned GPS route
- `cup_routewait(seconds)` — pause on the route
- `cup_speed(ratio, node_id=None)` — route speed ratio
- `cup_rudder_angle(angle, node_id=None)` — steering for vehicle mobility
- `cup_mapcenter(lon, lat)` — move the map so that (lon, lat) is at the center
  of the view (zoom unchanged); e.g. follow a node: `cup_mapcenter(*cup_getxy())`.
- `cup_drawroutes()` — draw all the project routes on the map

Node-to-node messaging (radio):
- `cup_send(message, dest=ALL)` — RADIO send, message WITHOUT spaces. To a
  node id (delivered only if that node is inside the sender's radio
  range, lost otherwise) or broadcast to the radio neighbors:
  `cup_send('A')`, `cup_send('A', ALL)`, `cup_send('A', '*')` are
  equivalent (a bare `*` is invalid Python). `ALL`/`BROADCAST` come from
  cup_functions.
- `cup_fsend(message, dest=ALL)` — forced send: same API but IGNORES the
  radio range (out-of-band channel: backbone/Internet). `cup_fsend('A', 3)`
  always reaches node 3; `cup_fsend('A')` reaches every node.
- `cup_read() -> str` — blocking receive

Agentic AI workflows bridge:
- `cup_toagent(txt, chid)` — fires every running workflow whose "CupCarbon
  Read" trigger has this chid (Channel ID, an int)
- `cup_fromagent(chid) -> str` — blocking wait for a "CupCarbon Send"
  workflow node with this chid. Only nodes already listening receive
  (real-time delivery; missed messages are lost)

Control:
- `cup_wait(seconds)` — pause (floats allowed: `cup_wait(0.5)`)
- `cup_stopsimulation()` — stop the whole IoT simulation

## Canonical patterns

Blink:
```python
from cup_functions import *
while True:
    cup_mark(); cup_wait(1)
    cup_unmark(); cup_wait(1)
```

Detector -> mobile responder (radio):
```python
# node 1 (detector)
from cup_functions import *
while True:
    if cup_dsensor():
        x, y = cup_getxy()
        cup_send(f"{x}#{y}", 2)      # '#' instead of spaces
        cup_wait(5)
    cup_wait(0.2)
```
```python
# node 2 (responder)
from cup_functions import *
while True:
    x, y = map(float, cup_read().split("#"))
    cup_moveto(x, y)
```

MQTT alert (publish own id when marked):
```python
from cup_functions import *
import paho.mqtt.client as mqtt
node_id = cup_getid()
c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"cup_{node_id}")
c.connect("broker.hivemq.com", 1883, 30); c.loop_start()
was = False
while True:
    m = cup_ismarked()
    if m and not was:
        c.publish("cupcarbon/fire", str(node_id), qos=1)
    was = m
    cup_wait(0.5)
```

MQTT-triggered driving (subscribe, then road-route to the sender):
```python
from cup_functions import *
import queue
import paho.mqtt.client as mqtt
node_id = cup_getid(); alerts = queue.Queue()
c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"cup_resp_{node_id}")
c.on_message = lambda cl, u, msg: alerts.put(int(msg.payload.decode()))
c.connect("broker.hivemq.com", 1883, 30)
c.subscribe("cupcarbon/fire", qos=1); c.loop_start()
while True:
    try:
        fid = alerts.get(timeout=0.5)
    except queue.Empty:
        cup_wait(0.1); continue
    if fid != node_id:
        cup_route(node_id, fid)      # road route to the alerting node
        cup_routego()
```

Ask an AI workflow for a decision (chid = 32 on both sides):
```python
from cup_functions import *
while True:
    cup_toagent(f"temperature {21 + cup_getid()}", 32)
    answer = cup_fromagent(32)       # JSON-ish text from the AI Agent
    cup_print(answer)
    cup_wait(2)
```

## Radio range: the #1 reason a scenario "does not work"

Messages are delivered only to nodes inside the radio range of the sender.
Before writing code, check the geometry: at these latitudes 0.001 deg of
latitude is ~111 m, and 0.001 deg of longitude is ~111 m x cos(latitude).
If a receiver is 98 m away and the range is 80 m, the code is correct but
nothing happens. Set it explicitly:

```
set iot 2 range 150        # console  (MCP: set_radio_range(2, 150))
```

Do not confuse the three radii: `range` = radio (communication, metres),
`size` = physical radius of the node (drawing only), `sensing` = detection
range of the sensor unit.

## Common mistakes (check these first when a script "does nothing")

- **No script assigned** — the centre of the node must be orange.
  Console: `set script 2 blink.py` (MCP: `assign_script`).
- **Radio range too small** — see above; the most frequent cause.
- **`cup_read()` blocks** — the loop stops there until a message arrives,
  so any `cup_wait()` placed after it does not run meanwhile. Nothing is
  displayed until the first message: this is normal, not a freeze.
- **Latching mark** — `if x=='A': cup_mark() else: cup_unmark()` keeps the
  node lit until a *different* message arrives. Either send an explicit
  "off" message (A/B alternating) or flash: `cup_mark(); cup_wait(0.5);
  cup_unmark()`.
- **Spaces in messages** — `cup_send` payloads must contain no spaces; use
  `#` or `,` as separator and split on reception.
- **Tabs in the file** — Python raises `TabError`; the editor shows tabs in
  pink, use 4 spaces (button Tabs -> Spaces).
- **Loop without `cup_wait`** — burns CPU and floods the map.
- **Python not found** — set `python3` in Executor Path Configuration.

## Reading back what a node runs

With the MCP server: `list_scripts()`, `read_script('send.py')`,
`get_node_code(2)` return the actual source, and `get_property(2, 'range')`
the radio range — useful to debug a scenario you did not write.

## Agentic AI workflows (the n8n-like editor)

Node scripts talk to workflows with `cup_toagent(msg, chid)` (fires the
"CupCarbon Read" trigger with the same chid) and `cup_fromagent(chid)`
(waits for a "CupCarbon Send" node with that chid). Workflows follow the
n8n item model: every node receives `[{a},{b},...]` and outputs
`[f(a),f(b),...]`; parameters accept `{{ $json.field }}` per item.
Useful nodes: AI Agent (Anthropic/OpenAI), If/Filter/Merge, HTTP Request,
**API Call** (base URL + path + query + auth preset: bearer, API key in
header or query, basic), **MCP Client** (calls a tool of an MCP server over
http or stdio; empty tool = list tools), **MCP Server Trigger** (exposes the
workflow as one MCP tool on http://localhost:5690/mcp).

To create a workflow through the MCP server: call `workflow_node_types()`
first (exact type ids and config keys — never guess them), then
`workflow_put(name, json)` with
`{"nodes":[{"id","type","x","y","config"}],"connections":[{"from","to","fromPort"}]}`
(`fromPort` = "output", or "true"/"false" for If; never connect TO a
trigger). Node pictures: MCP `set_image(id, url)` = `cup_image(url)`.

## Driving CupCarbon through the MCP server: batch, don't loop

Each MCP tool call is one round trip. For several operations of the same
kind, use ONE batch call:

- `add_nodes([{"type":"iot","lat":..,"lon":..,"script":"patrol.py","range":150,"icon":13}, ...])`
  creates everything (scripts, ranges, icons, pictures applied at creation)
  in one message, one undo step, and returns `{"ids":[...]}` for the next calls;
- `set_properties(ids=[1,2,3], props={"script":"rec.py","range":120})`;
- `move_nodes([...])`, `delete_objects([...])`, `mark_nodes([...])`;
- `run_batch(["project status", "set script 1 send.py", "sim iot start"])`
  for a mix of commands, in order.

Typical scenario in 3 calls: `write_script` (once per script), `add_nodes`
(all the nodes with their scripts), `run_simulation`.

## Output expectations
Produce a complete runnable script per node role (starting with the import
line), name the files (e.g. `detector.py`, `responder.py`), and state which
node each is assigned to. Mention `pip install paho-mqtt` when MQTT is used
and that `cup_route` needs internet. If the user has the CupCarbon MCP
server connected, offer to save and assign the scripts with its
write_script / assign_script tools — checking first with project_status()
that a project is open (CupCarbon refuses to add or modify anything
without one; create it with project_new).
