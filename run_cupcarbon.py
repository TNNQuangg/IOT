"""Run the seven CupCarbon scenarios for ten active wall-clock minutes each."""

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path
import hashlib
import msvcrt
import os
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / "cupcarbon_runtime"
JAR = RUNTIME / "cupcarbon.jar"
SCENARIOS = ("Troi quang", "Mua 12%", "Mua 25%", "Sat lo cham",
             "Sat lo nhanh", "S3 hong", "Sat lo nhanh va S5 hong")
EVENT = re.compile(r"\[(GEN|GW|DROP|FAIL|DETECT|REPAIR_TX|BYPASS_ON|CONFIRM|REVERT)\]")
FIELD = re.compile(r"(\w+)=\s*([\w.+-]+)")


def set_case(path, scenario):
    data = path.read_bytes()
    data, count = re.subn(rb"(?m)^set SCENARIO \d+", f"set SCENARIO {scenario}".encode(), data)
    if count != 1:
        raise ValueError(f"Expected one SCENARIO setting in {path}")
    path.write_bytes(data)


def prepare_project(case, scenario):
    project = case / "landslide_lora"
    shutil.copytree(ROOT / "landslide_lora", project, ignore=shutil.ignore_patterns("logs", "results"))
    (project / "logs").mkdir()
    (project / "results").mkdir()
    sensor = project / "scripts" / "script_sensor_node.csc"
    sink = project / "scripts" / "script_sink_node.csc"
    for script in (sensor, sink):
        set_case(script, scenario)
    # Disable the legacy pre-announced switch. Keep the node's own failure
    # schedule and the existing silence/REPAIR exchange.
    source = sensor.read_bytes()
    source, count = re.subn(rb"(?m)^  if \(FAIL_NODE > 0\)", b"  if (0 == 1)", source)
    if count != 1:
        raise ValueError("Could not identify the pre-announced bypass in the sensor script")
    sensor.write_bytes(source)
    return project


def summarize(path, scenario):
    generated, received, counts, alarm_delays = {}, {}, Counter(), []
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            match = EVENT.search(line)
            if not match:
                continue
            tag = match[1]
            data = dict(FIELD.findall(line[match.end():]))
            counts[tag] += 1
            if tag in ("GEN", "GW") and {"src", "seq", "flag", "t"} <= data.keys():
                key = int(float(data["src"])), int(float(data["seq"]))
                flag = int(float(data["flag"]))
                if flag in (0, 100, 255):
                    target = generated if tag == "GEN" else received
                    target.setdefault(key, (flag, float(data["t"])))
    delivered = generated.keys() & received.keys()
    if not generated or not delivered:
        raise ValueError(f"No complete GEN/GW packet pairs in {path}")
    alarms = {key for key, (flag, _) in generated.items() if flag == 255 and key[0] == 5}
    alert_delivered = alarms & delivered
    alarm_delays = [received[key][1] - 73 for key in alert_delivered]
    average = sum(received[k][1] - generated[k][1] for k in delivered) / len(delivered)
    lines = [f"PDR {len(delivered) / len(generated):.2%} ({len(delivered)}/{len(generated)})",
             f"Mean latency from GEN: {average:.3f} simulated s (received packets only)"]
    for node in range(1, 11):
        gen_count = sum(src == node for src, _ in generated)
        rx_count = sum(src == node for src, _ in delivered)
        ratio = f"{rx_count / gen_count:.2%}" if gen_count else "NA"
        lines.append(f"  S{node}: {rx_count}/{gen_count} ({ratio})")
    if scenario in (3, 4, 6):
        first = min(alarm_delays, default=None)
        lines.append(f"Alert packets: {len(alert_delivered)}/{len(alarms)} (FLAG 255 from S5)")
        delay = f"{first:.3f} simulated s" if first is not None else "none"
        lines.append(f"First alert from event onset: {delay} | within 30 s: "
                     f"{'YES' if first is not None and first <= 30 else 'NO'}")
    lines.append("Events: " + ", ".join(f"{key}={count}" for key, count in counts.items()))
    return lines


def execute(published, folder, args):
    def append(message):
        for path in dict.fromkeys((folder / "log.txt", published)):
            with path.open("a", encoding="utf-8") as stream:
                stream.write(message + "\n")
        print(message, flush=True)

    append("CUPCARBON KLAINES | batch " + folder.name)
    append(f"Requested active duration per scenario: {args.wall_seconds} wall-clock s")
    append(f"Engine pacing: {args.pace} ms per simulated s (nominal, negative sleeps clamped to zero). "
           "Use the measured simulated horizon in each result.")
    append("Model: CupCarbon engine + existing SenScript project, legacy packet loss, "
           "no ACK, MAC disabled, pre-announced bypass disabled.")
    append("One run per scenario. No controlled seed, confidence interval or V3 PHY/energy claim.")
    append(f"Detailed logs: {folder}")
    if not JAR.is_file():
        append(f"ERROR: missing installed CupCarbon JAR: {JAR}")
        return 1
    java_home = os.environ.get("JAVA_HOME")
    compiler = Path(java_home) / "bin" / "javac.exe" if java_home else None
    if compiler is None or not compiler.is_file():
        executable = shutil.which("javac")
        compiler = Path(executable).resolve() if executable else None
    if compiler is None:
        append("ERROR: javac is required. Install a JDK and put its bin directory on PATH.")
        return 1
    java = Path(compiler).resolve().with_name("java.exe")
    with JAR.open("rb") as jar:
        append("cupcarbon.jar SHA-256: " + hashlib.file_digest(jar, "sha256").hexdigest())
    classes = folder / "classes"
    classes.mkdir()
    compile_log = folder / "compile.log"
    try:
        with compile_log.open("wb") as out:
            subprocess.run([str(compiler), "-encoding", "UTF-8", "-cp", str(JAR), "-d", str(classes),
                            str(ROOT / "CupCarbonBatch.java"), str(ROOT / "CupCarbonPacing.java")],
                           stdout=out, stderr=subprocess.STDOUT, timeout=60, check=True)
            subprocess.run([str(java), "-cp", str(classes), "CupCarbonPacing", str(JAR), str(classes)],
                           stdout=out, stderr=subprocess.STDOUT, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError):
        append(f"ERROR: CupCarbon batch setup failed, see {compile_log}. The pacing guard requires JDK 24+.")
        return 1
    failures = 0
    for scenario in (range(7) if args.scenario is None else [args.scenario]):
        case = folder / f"KB-{scenario}"
        case.mkdir()
        raw = case / "cupcarbon.log"
        append(f"\nKB-{scenario} | {SCENARIOS[scenario]} | START {datetime.now().isoformat(timespec='seconds')}")
        append(f"Engine log: {raw}")
        try:
            project = prepare_project(case, scenario)
            with raw.open("wb") as output:
                subprocess.run([str(java), "-Dfile.encoding=UTF-8", "-Djava.io.tmpdir=.",
                                "-Duser.home=.", "-cp", f"{classes};{JAR}",
                                "CupCarbonBatch", str(project), str(args.wall_seconds), str(args.pace)],
                               cwd=RUNTIME, stdout=output, stderr=subprocess.STDOUT,
                               check=True, timeout=args.wall_seconds + 120)
            end = re.search(r"^\[BATCH_END\] active_wall_s=([\d.]+) sim_s=([\d.]+)",
                            raw.read_text(encoding="utf-8", errors="replace"), re.M)
            if not end or float(end[1]) < args.wall_seconds or float(end[2]) <= 0:
                raise ValueError("CupCarbon did not report a completed active window")
            append(f"Active runtime: {end[1]} wall-clock s | simulated horizon: {end[2]} s")
            append("\n".join(summarize(raw, scenario)))
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            failures += 1
            append(f"ERROR: {error}. See {raw}")
    append(f"\nFinished {datetime.now().isoformat(timespec='seconds')} | failed scenarios: {failures}")
    return int(bool(failures))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=int, choices=range(7))
    parser.add_argument("--wall-seconds", type=int, default=600,
                        help="Override for validation runs; short runs use a separate log")
    parser.add_argument("--pace", type=int, default=450, help="CupCarbon visual pacing in ms/s")
    args = parser.parse_args()
    if args.wall_seconds <= 0 or args.pace <= 0:
        parser.error("Both durations must be positive")
    base = ROOT / "results_cupcarbon"
    base.mkdir(exist_ok=True)
    with (base / "batch.lock").open("a+b") as lock:
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            print("A CupCarbon batch is already running.", file=sys.stderr)
            return 1
        folder = base / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        folder.mkdir()
        full = args.wall_seconds == 600 and args.scenario is None
        log = ROOT / "log.txt" if full else folder / "log.txt"
        if log.exists():
            shutil.copy2(log, folder / "previous_log.txt")
            log.write_text("", encoding="utf-8")
        return execute(log, folder, args)


if __name__ == "__main__":
    raise SystemExit(main())
