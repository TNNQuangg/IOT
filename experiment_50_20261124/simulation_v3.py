"""Deterministic discrete-event model for KICH_BAN_MO_PHONG_V3.md."""

from collections import Counter, deque
from dataclasses import dataclass, field
from heapq import heappop, heappush
from itertools import count
from math import ceil
from random import Random

GW = 11
GEN_END, END, LANDSLIDE, DEADLINE = 1000, 1300, 73, 30
ZONE = {4, 5, 6, 7}


def airtime(payload=9, sf=7, bandwidth=125000, coding=1, preamble=8):
    symbol = 2**sf / bandwidth
    low_rate = int(symbol >= 0.016)
    symbols = 8 + max(0, ceil((8 * payload - 4 * sf + 28 + 16) /
                              (4 * (sf - 2 * low_rate))) * (coding + 4))
    return (preamble + 4.25 + symbols) * symbol


AIRTIME = airtime()


def position(node):
    return 0 if node == GW else node * 50


def downstream(node):
    return GW if node == 1 else node - 1


def child_of(node):
    return 1 if node == GW else node + 1


@dataclass(frozen=True)
class Config:
    name: str = "FULL"
    profile: str = "LORA_STRESS"
    fixed: int = 0
    alarm_copies: int = 3
    repeat: bool = True
    escalate: bool = True
    bypass: bool = True
    detect: bool = True
    oracle: bool = False
    l0: int = 5
    silence: int = 90
    jitter: tuple = (0.1, 0.4)
    tau: float = 1
    interference: int = 120


@dataclass(frozen=True)
class Packet:
    src: int
    seq: int
    flag: int
    value: int
    gen: float

    @property
    def key(self):
        return self.src, self.seq


@dataclass
class Node:
    hop: int
    alive: bool = True
    seen: set = field(default_factory=set)
    queue: deque = field(default_factory=deque)
    seq: int = 0
    busy: bool = False
    stable: int = 0
    previous: int = 20
    alert_until: float = 0
    sample_version: int = 0
    last_heard: float = 0
    repair_version: int = 0
    repair_open: bool = False
    confirmed: bool = False
    tx_seconds: float = 0
    alive_until: float = END


class Channel:
    """Poisson refresh implements good/bad CTMC with rates p/tau and (1-p)/tau."""

    def __init__(self, seed, scenario, config):
        self.seed, self.scenario, self.config = seed, scenario, config
        self.links = {}

    def weather(self, time):
        if self.scenario in (1, 2) and 26 <= time < 200:
            return 0.12 if self.scenario == 1 else 0.25
        if self.scenario in (3, 4, 6) and time >= 26:
            return 0.12
        return 0

    def probability(self, source, dest, time, target):
        probability = self.weather(time)
        if self.scenario in (3, 4, 6) and time >= LANDSLIDE and {source, dest} & ZONE:
            fraction = min(1, (time - LANDSLIDE) / 60) if self.scenario == 3 else 1
            probability += (target - probability) * fraction
        if abs(position(source) - position(dest)) == 100:
            probability = min(0.95, probability + 0.10)
        return probability

    def lost(self, source, dest, time, copy_id):
        key = source, dest
        if key not in self.links:
            rng = Random(f"channel:{self.seed}:{source}:{dest}")
            target = rng.uniform(0.40, 0.50) if self.scenario == 3 else rng.uniform(0.80, 0.85)
            bad = rng.random() < self.probability(source, dest, 0, target)
            self.links[key] = [rng, target, bad, rng.expovariate(1 / self.config.tau)]
        state = self.links[key]
        rng, target, bad, refresh = state
        if self.config.profile == "LEGACY_IID":
            draw = Random(f"iid:{self.seed}:{source}:{dest}:{copy_id}").random()
            return draw < self.probability(source, dest, time, target)
        while refresh <= time:
            bad = rng.random() < self.probability(source, dest, refresh, target)
            refresh += rng.expovariate(1 / self.config.tau)
        # The specification resets a link immediately when p drops to zero.
        if self.probability(source, dest, time, target) == 0:
            bad = False
        state[2:] = [bad, refresh]
        return bad


@dataclass
class Transmission:
    source: int
    dest: int
    packet: Packet
    copy_id: str
    start: float
    end: float
    reasons: set
    cancelled: bool = False


class Simulation:
    def __init__(self, scenario, seed, config, trace=None):
        self.scenario, self.seed, self.config, self.trace = scenario, seed, config, trace
        self.time = 0
        self.events, self.active = [], {}
        self.order = count()
        self.channel = Channel(seed, scenario, config)
        self.nodes = {i: Node(downstream(i) if i != GW else 0) for i in range(1, 12)}
        self.sensor_rng = {i: Random(f"sensor:{seed}:{i}") for i in range(1, 11)}
        self.generated, self.delivered = {}, {}
        self.live_copies = Counter()
        self.drops, self.link_tx, self.link_rx = Counter(), Counter(), Counter()
        self.route_events = []
        self.failure = {5: (90, 3), 6: (93, 5)}.get(scenario)
        self.has_alarm = scenario in (3, 4, 6)

    def log(self, event, node=0, packet=None, **details):
        if self.trace is None:
            return
        if packet:
            details.update(src=packet.src, seq=packet.seq, flag=packet.flag,
                           tgen=packet.gen, event_id=1 if packet.flag == 255 else None)
        self.trace(dict(event=event, t=round(self.time, 9), node=node, **details))

    def schedule(self, when, callback, *args, priority=2):
        if when <= END:
            heappush(self.events, (when, priority, next(self.order), callback, args))

    def new_packet(self, node, flag, value):
        state = self.nodes[node]
        state.seq += 1
        packet = Packet(node, state.seq, flag, value, self.time)
        self.log("GEN", node, packet)
        if flag in (0, 100, 255):
            self.generated[packet.key] = packet
        return packet

    def sample(self, node, version):
        state = self.nodes[node]
        if not state.alive or version != state.sample_version or self.time >= GEN_END:
            return
        value = 20 + self.sensor_rng[node].randint(-2, 2)
        if self.channel.weather(self.time) and node in ZONE:
            value += 22
        if self.has_alarm and node == 5 and self.time >= LANDSLIDE:
            value = self.sensor_rng[node].randint(88, 92)
        delta = abs(value - state.previous)
        state.previous = value
        flag = 255 if value >= 85 else 100 if value >= 40 else 0
        if flag == 255 or self.time < state.alert_until or delta >= 5:
            state.stable, level = 0, 0
        elif flag == 100:
            state.stable, level = 0, 1
        else:
            state.stable += 1
            level = 2 if state.stable >= 6 else 1 if state.stable >= 3 else 0
        period = self.config.fixed or (self.config.l0, 15, 30)[level]
        self.log("LEVEL", node, level=level, period=period)
        self.enqueue(node, self.new_packet(node, flag, value if flag else delta))
        self.schedule(self.time + period, self.sample, node, version)

    def enqueue(self, node, packet, dest=None):
        state = self.nodes[node]
        copies = {0: 1, 100: 2, 255: self.config.alarm_copies, 150: 3, 200: 3}
        number = copies[packet.flag] if self.config.repeat else 1
        self.live_copies[packet.key] += number
        state.queue.append((packet, dest, 1, number))
        self.begin(node)

    def begin(self, node):
        state = self.nodes[node]
        if not state.alive or state.busy or not state.queue:
            return
        packet, dest, copy, total = state.queue.popleft()
        dest = dest if dest is not None else state.hop
        copy_id = f"{packet.src}:{packet.seq}:{node}:{copy}"
        reasons = set()
        if not self.nodes[dest].alive:
            reasons.add("NODE_DEAD")
        if self.channel.lost(node, dest, self.time, copy_id):
            reasons.add("CHANNEL")
        tx = Transmission(node, dest, packet, copy_id, self.time, self.time + AIRTIME, reasons)
        if self.config.profile != "LEGACY_IID":
            for other in self.active.values():
                if other.dest == node:
                    other.reasons.add("HALF_DUPLEX")
                if other.source == dest:
                    tx.reasons.add("HALF_DUPLEX")
                if abs(position(node) - position(other.dest)) <= self.config.interference:
                    other.reasons.add("COLLISION")
                if abs(position(other.source) - position(dest)) <= self.config.interference:
                    tx.reasons.add("COLLISION")
        state.busy = True
        self.active[node] = tx
        self.link_tx[(node, dest)] += 1
        self.log("TX_START", node, packet, to=dest, copy_id=copy_id, ttx=tx.start)
        self.log("RADIO_STATE", node, state="TX")
        self.schedule(tx.end, self.finish, tx, copy, total, priority=1)

    def finish(self, tx, copy, total):
        if tx.cancelled:
            return
        state = self.nodes[tx.source]
        del self.active[tx.source]
        state.tx_seconds += tx.end - tx.start
        self.live_copies[tx.packet.key] -= 1
        self.log("TX_END", tx.source, tx.packet, to=tx.dest, copy_id=tx.copy_id, ttx=tx.start)
        self.log("RADIO_STATE", tx.source, state="RX")
        if tx.reasons:
            cause = next(reason for reason in ("NODE_DEAD", "RADIO_OFF", "HALF_DUPLEX",
                                               "COLLISION", "CHANNEL") if reason in tx.reasons)
            self.drops[cause] += 1
            self.log("DROP", tx.dest, tx.packet, source=tx.source, to=tx.dest, cause=cause,
                     reasons=sorted(tx.reasons), copy_id=tx.copy_id, ttx=tx.start)
        else:
            self.link_rx[(tx.source, tx.dest)] += 1
            self.log("RX_OK", tx.dest, tx.packet, source=tx.source, to=tx.dest,
                     copy_id=tx.copy_id, ttx=tx.start)
            self.schedule(self.time, self.receive, tx)
        if copy < total:
            state.queue.appendleft((tx.packet, None if tx.packet.flag != 200 else tx.dest,
                                    copy + 1, total))
            rng = Random(f"jitter:{self.seed}:{tx.copy_id}")
            self.schedule(self.time + rng.uniform(*self.config.jitter), self.release, tx.source)
        else:
            self.schedule(self.time, self.release, tx.source)

    def release(self, node):
        self.nodes[node].busy = False
        self.begin(node)

    def route_log(self, event, node, **details):
        self.route_events.append(dict(event=event, t=self.time, node=node, **details))
        self.log(event, node, **details)

    def receive(self, tx):
        node, packet = tx.dest, tx.packet
        state = self.nodes[node]
        child = child_of(node)
        if packet.flag == 200:
            if (not self.config.bypass or node < 2 or node == GW
                    or tx.source != downstream(node - 1) or packet.value not in (0, node - 1)):
                return
        elif tx.source != child and not (self.config.bypass and tx.source == child + 1
                                         and state.repair_open):
            return
        if packet.flag != 200 and tx.source == child:
            state.last_heard = self.time
            if state.repair_open:
                state.repair_open = state.confirmed = False
                state.repair_version += 1
                self.route_log("REVERT", node, child=child)
                if child < 10:
                    self.enqueue(node, self.new_packet(node, 200, 0), child + 1)
        if packet.key in state.seen:
            self.log("DUP", node, packet)
            return
        state.seen.add(packet.key)
        if packet.flag == 200:
            state.hop = tx.source if packet.value else downstream(node)
            if packet.value:
                self.route_log("BYPASS_ON", node, to=state.hop)
            return
        if tx.source == child + 1 and not state.confirmed and packet.flag in (0, 100, 255):
            state.confirmed = True
            self.route_log("CONFIRM", node, child=child)
        if node == GW:
            self.delivered[packet.key] = self.time
            self.log("GW", node, packet, lat=self.time - packet.gen, copy_id=tx.copy_id)
            return
        if self.config.escalate and not self.config.fixed and packet.flag in (255, 150):
            if self.time >= state.alert_until:
                state.sample_version += 1
                self.schedule(self.time + self.config.l0, self.sample, node, state.sample_version)
            state.alert_until = self.time + 60
        self.enqueue(node, packet)

    def silence_check(self, node):
        if not self.config.detect:
            return
        state = self.nodes[node]
        child = child_of(node)
        if not state.alive or child > 10:
            return
        if not state.repair_open and self.time - state.last_heard >= self.config.silence:
            state.repair_open = True
            state.repair_version += 1
            self.route_log("DETECT", node, child=child)
            if node != GW:
                self.enqueue(node, self.new_packet(node, 150, child))
            if self.config.bypass and child < 10:
                for attempt in range(3):
                    self.schedule(self.time + 5 * attempt, self.repair, node, child, state.repair_version)
                self.schedule(self.time + 100, self.unreachable, node, child, state.repair_version)
        if self.time + 1 < GEN_END:
            self.schedule(self.time + 1, self.silence_check, node)

    def repair(self, node, child, version):
        state = self.nodes[node]
        if state.alive and state.repair_version == version and not state.confirmed:
            self.route_log("REPAIR_TX", node, child=child)
            self.enqueue(node, self.new_packet(node, 200, child), child + 1)

    def unreachable(self, node, child, version):
        state = self.nodes[node]
        if state.alive and state.repair_version == version and not state.confirmed:
            self.route_log("UNREACHABLE", node, child=child)

    def fail(self, node):
        state = self.nodes[node]
        state.alive, state.alive_until = False, self.time
        for packet, _, copy, total in state.queue:
            self.live_copies[packet.key] -= total - copy + 1
        state.queue.clear()
        tx = self.active.pop(node, None)
        if tx:
            tx.cancelled = True
            state.tx_seconds += self.time - tx.start
            self.live_copies[tx.packet.key] -= 1
            self.drops["NODE_DEAD"] += 1
            self.log("DROP", tx.dest, tx.packet, source=node, to=tx.dest,
                     cause="NODE_DEAD", reasons=["NODE_DEAD"], copy_id=tx.copy_id, ttx=tx.start)
        for transmission in self.active.values():
            if transmission.dest == node:
                transmission.reasons.add("NODE_DEAD")
        self.route_log("FAIL", node, configured=self.time)
        self.log("RADIO_STATE", node, state="OFF")
        if self.config.oracle and node < 10:
            self.nodes[node + 1].hop = downstream(node)
            self.nodes[downstream(node)].repair_open = True
            self.route_log("BYPASS_ON", node + 1, to=downstream(node))

    def run(self):
        self.log("RUN_START")
        for node in self.nodes:
            self.log("RADIO_STATE", node, state="RX")
            if node != GW:
                phase = Random(f"phase:{self.seed}:{node}").uniform(0, 5)
                self.schedule(phase, self.sample, node, 0)
            if self.config.detect:
                self.schedule(1, self.silence_check, node)
        if self.failure:
            when, node = self.failure
            self.schedule(when, self.fail, node, priority=0)
        while self.events:
            self.time, _, _, callback, args = heappop(self.events)
            callback(*args)
        for tx in self.active.values():
            self.nodes[tx.source].tx_seconds += END - tx.start
        self.time = END
        self.log("RUN_END")
        return self.summary()

    def summary(self):
        def metrics(packets):
            lats = sorted(self.delivered[p.key] - p.gen for p in packets if p.key in self.delivered)
            return dict(gen=len(packets), received=len(lats),
                        before_cutoff=sum(self.delivered.get(p.key, END) < GEN_END for p in packets),
                        pending=sum(p.key not in self.delivered and self.live_copies[p.key] > 0
                                    for p in packets),
                        pdr=len(lats) / len(packets) if packets else None,
                        latency=sum(lats) / len(lats) if lats else None,
                        p50=lats[ceil(len(lats) * .50) - 1] if lats else None,
                        p95=lats[ceil(len(lats) * .95) - 1] if lats else None)

        packets = list(self.generated.values())
        alarms = [p for p in packets if p.flag == 255]
        first = min((self.delivered[p.key] - LANDSLIDE for p in alarms if p.key in self.delivered),
                    default=None)
        radio = {}
        for node, state in self.nodes.items():
            rx = state.alive_until - state.tx_seconds
            radio[node] = dict(tx=state.tx_seconds, rx=rx, off=END - state.alive_until,
                               duty_cycle=state.tx_seconds / END,
                               energy={rho: state.tx_seconds + rho * rx for rho in (.2, .4, .8)})
        return dict(seed=self.seed, network=metrics(packets), alarm=metrics(alarms),
                    alarm_delay=first, alarm_on_time=(first is not None and first <= DEADLINE)
                    if self.has_alarm else None, radio=radio, drops=dict(self.drops),
                    nodes={node: metrics([p for p in packets if p.src == node]) for node in range(1, 11)},
                    flags={flag: metrics([p for p in packets if p.flag == flag]) for flag in (0, 100, 255)},
                    routes=self.route_events,
                    links={f"{a}-{b}": dict(tx=n, rx=self.link_rx[(a, b)])
                           for (a, b), n in self.link_tx.items()})
