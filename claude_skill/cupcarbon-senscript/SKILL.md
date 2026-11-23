---
name: cupcarbon-senscript
description: Write SenScript programs for CupCarbon WSN sensor nodes. Use when the user asks for SenScript code, .csc scripts, CupCarbon WSN node behaviors (mark, send/receive, routing, sensing, leader election, radio parameters) for the classical sensor nodes of the CupCarbon simulator.
---

# CupCarbon SenScript coding (WSN environment)

SenScript is the built-in script of CupCarbon's classical WSN sensor nodes
(one command per line, no external language). Scripts are saved as `.csc`
files in the project's `scripts/` folder (the SenScript editor adds the
extension automatically) and assigned per node in Device Parameters. A
project is either WSN (SenScript) or IoT (Python cup_*) — never both.

## Language rules
- Variables are untyped, created by `set` and referenced by NAME in
  commands (`print x`) or `$`-free expressions inside `set` (`set z x+y`).
- `loop` starts the section repeated forever; `stop` ends the script.
- Conditions must be FULLY parenthesized:
  `if ((x==1) && (y>0))` — never `if (x==1 && y>0)`. Close blocks with `end`.
- Structured messages use `#` as separator: build with `data`, split with
  `rdata`. Stacks use `&` (`sadd`/`spop`/`nth`).
- `delay` is in milliseconds (simulated time).
- `receive x` is the blocking read (use it, `wait` is deprecated);
  `read x` is non-blocking; `pick x` reads without consuming.

## Command reference (essentials)

Variables & math: `set x 5` | `set z (x*y)/3` | `inc x` / `dec x` |
`int x a` | `conc x a b` | `max/min x a b` |
`math f y x` (sqrt,sin,cos,tan,asin,acos,atan,abs,pow,log,log10,exp) |
`rand x` | `randb x lo hi` | `rgauss x` | `hash x s` |
`charat c s i` | `length v s` |
logic `and/or/xor/not x a b` | bitwise `band/bor/bxor/bnot x a b`

Control: `loop` | `stop` | `if (...) ... [else ...] end` |
`while (...) ... end` | `for i 0 10 [step] ... end` |
`goto <line|label>` (label: `B:set x 12`) | `function x name args`

Tables & data: `tab t r c` / `tget x t i j` / `tset v t i j` |
`vec v n` / `vget x v i` / `vset val v i` |
`data p a b c` (p=a#b#c) | `rdata p a b c` | `vdata v a#b#c` |
`sadd x t` / `spop v t` / `nth v i t` |
`smin m x y` / `smax m x y` (on id#value messages — elections)

Sensing: `areadsensor s` (analog; s=X if nothing, else S#id#value — use
rdata) | `dreadsensor x` (1 if event/mobile detected) |
`getpos p` (lon#lat) / `getpos2 x y` | `getinfo p` (detected mobile
id#lon#lat) | `rotate x t` (directional sensor)

Radio: `atch n` (channel) | `atid n` | `atmy n` (MY address) |
`atnid n` (network id) | `atpl p` (power %, reduces range) |
`atnd n [v]` (neighbor count [+ id vector]) |
`atget id|my|ch|nid x` | `drssi x` | `distance x id` |
`radio <module_name>` (switch radio module/standard)

Messages: `send p 2` (to id 2) | `send p` or `send p *` (broadcast) |
`send p * 3` (broadcast except id 3) | `send p 0 4` (to MY address 4) |
`send p 0 0 5` (direct/cellular-like) | `receive x [timeout_ms]` |
`read x` | `pick x` | `buffer x` | `cbuffer`

Card & display: `delay ms` | `mark 1|0` | `led pin color` (0=unmark,
1=mark, 2..14 colors) | `print ...` | `cprint ...` (console) |
`printfile ...` (results file) | `battery x` / `battery set x` |
`time x` | `kill prob` | `script name` / `rscript name` (load another
.csc keeping / resetting variables) | `edge 1|0 id` (mark a link)

Mobility & simulation: `move lat lon z speed` | `rmove t` (next route
point after t ms; Mobility checkbox required) | `route name` |
`angle2 a x1 y1 x2 y2 x3 y3` | `simulation sspeed|aspeed v`

## Canonical patterns

Blink:
```
loop
mark 1
delay 1000
mark 0
delay 1000
```

Transmitter / receiver:
```
loop            // transmitter (node 1)
send "A" 2
delay 1000
send "B" 2
delay 1000
```
```
loop            // receiver (node 2)
receive v
if(v=="A")
mark 1
else
mark 0
end
```

Generic router (same script for every router — broadcast except sender):
```
atget id id
loop
receive rp
rdata rp rid v
data p id v
send p * rid
```

Read an analog sensor and alert:
```
loop
areadsensor v
if(v!="X")
rdata v a b c
if(c>30)
send "ALERT" *
end
end
delay 1000
```

Leader election (max value; also works with ids or coordinates):
```
randb x 0 1000
mark 1
set vmax x
send vmax
loop
receive v
if (v > vmax)
mark 0
set vmax v
send v
end
delay 1
```

## Common mistakes (check these first when a script "does nothing")

- **No script assigned** to the node (Device Parameters > Script file).
- **Radio range too small**: `send`/`receive` only reach nodes inside the
  radio range — check the distances before suspecting the code.
- **`receive` blocks** until a message arrives: the node stays idle, which
  is normal.
- **No `delay` in a `loop`**: floods the simulation.
- **`mark 1` never cleared**: add `mark 0` on the opposite condition.
- A **WSN** project cannot contain IoT nodes (and vice versa).

## Output expectations
Produce one complete `.csc` script per node role, with the file name and
the node it is assigned to. Do not indent with tabs (spaces are fine;
indentation is cosmetic in SenScript). Remind the user to run the WSN
simulation (Run Simulation) and, for mobility/events, to activate the
Mobility/Events checkbox. For IoT nodes / Python, use the
cupcarbon-coding skill instead.
