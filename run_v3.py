"""Batch runner and reproducible summaries for the V3 model."""

import argparse
import csv
import hashlib
import itertools
import json
import math
from dataclasses import asdict, replace
from datetime import datetime
from pathlib import Path
from random import Random
import shutil
from statistics import mean, stdev
import subprocess
import sys
from time import perf_counter

from simulation_v3 import AIRTIME, END, GEN_END, Config, Simulation


ROOT = Path(__file__).resolve().parent
ALARM_SCENARIOS = (3, 4, 6)
NAMES = (
    "Trời quang", "Mưa 12%", "Mưa 25%", "Sạt lở chậm", "Sạt lở nhanh",
    "S3 hỏng", "Sạt lở nhanh và S5 hỏng",
)


def wilson(success, count):
    p = success / count
    z = 1.95996398454
    factor = 1 + z * z / count
    center = (p + z * z / (2 * count)) / factor
    half = z * math.sqrt(p * (1 - p) / count + z * z / (4 * count**2)) / factor
    return max(0, center - half), min(1, center + half)


def stats(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    n = len(values)
    rng = Random(1027)
    samples = sorted(mean(rng.choices(values, k=n)) for _ in range(2000))
    return dict(mean=mean(values), sd=stdev(values) if n > 1 else None,
                ci95=(samples[49], samples[1949]) if n > 1 else None, n=n)


def configurations(scenario, profile, controls):
    full = Config(profile=profile)
    variants = [full]
    if not controls:
        return variants
    variants.extend([replace(full, name="FIXED_5", fixed=5),
                     replace(full, name="FIXED_30", fixed=30),
                     replace(full, name="NO_REPEAT", repeat=False)])
    if scenario in ALARM_SCENARIOS:
        variants.append(replace(full, name="NO_ESCALATE", escalate=False))
    if scenario in (5, 6):
        variants.extend([replace(full, name="NO_BYPASS", bypass=False),
                         replace(full, name="ORACLE_BYPASS", oracle=True)])
    return variants


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def run_group(folder, scenario, config, seeds, trace=False, stage="benchmark"):
    started = perf_counter()
    group = folder / stage / f"KB-{scenario}" / config.name
    group.mkdir(parents=True)
    runs = []
    for seed in seeds:
        run = group / f"seed-{seed}"
        run.mkdir()
        tick = perf_counter()
        if trace:
            with (run / "events.jsonl").open("w", encoding="utf-8") as stream:
                def log(event):
                    stream.write(json.dumps(dict(run_id=f"{stage}/KB-{scenario}/{config.name}/{seed}",
                                                 **event), ensure_ascii=False) + "\n")
                result = Simulation(scenario, seed, config, log).run()
        else:
            result = Simulation(scenario, seed, config).run()
        result["wall_seconds"] = perf_counter() - tick
        write_json(run / "manifest.json", dict(
            scenario=scenario, seed=seed, config=asdict(config), python=sys.version,
            rng="Python Random (MT19937), independent named streams",
            model_sha256=MODEL_HASH, activity_end=GEN_END, simulation_end=END,
            clock="discrete events in seconds", wall_seconds=result["wall_seconds"],
            acceleration=END / result["wall_seconds"], radio=dict(
                frequency_mhz=868, power_dbm=14, sf=7, bw_hz=125000, cr="4/5",
                preamble=8, header="explicit", crc=True, payload_bytes=9, airtime=AIRTIME)))
        write_json(run / "metrics.json", result)
        runs.append(result)
    return dict(config=config.name, wall_seconds=perf_counter() - started, runs=runs)


MODEL_HASH = hashlib.sha256((ROOT / "simulation_v3.py").read_bytes()).hexdigest()


def weakest_energy(run, rho=.4):
    return max(run["radio"][i]["energy"][rho] for i in range(1, 11))


def group_summary(scenario, group, reference=None):
    runs = group["runs"]
    alarm = None
    if scenario in ALARM_SCENARIOS:
        success = sum(run["alarm_on_time"] for run in runs)
        alarm = dict(success=success, n=len(runs), ci95=wilson(success, len(runs)))
    result = dict(config=group["config"], n=len(runs), wall_seconds=group["wall_seconds"],
                  pdr=stats([r["network"]["pdr"] for r in runs]),
                  latency=stats([r["network"]["latency"] for r in runs]),
                  alarm_pdr=stats([r["alarm"]["pdr"] for r in runs]),
                  alarm_delay=stats([r["alarm_delay"] for r in runs]), alarm=alarm,
                  gen=sum(r["network"]["gen"] for r in runs),
                  received=sum(r["network"]["received"] for r in runs),
                  before_cutoff=sum(r["network"]["before_cutoff"] for r in runs),
                  pending=sum(r["network"]["pending"] for r in runs),
                  energy={rho: stats([weakest_energy(r, rho) for r in runs]) for rho in (.2, .4, .8)},
                  nodes={node: stats([r["nodes"][node]["pdr"] for r in runs])
                         for node in range(1, 11)},
                  paired_pdr_delta=stats([r["network"]["pdr"] - b["network"]["pdr"]
                                          for r, b in zip(runs, reference)])
                  if reference is not None and group["config"] != "FULL" else None)
    return result


def pct(value):
    return "NA" if value is None else f"{100 * value:.2f}%"


def metric(value, format_value=pct):
    if not value:
        return "NA"
    label = format_value(value["mean"])
    if value["ci95"]:
        low, high = value["ci95"]
        label += f" (CI95% {format_value(low)} – {format_value(high)})"
    return label


def report_group(group):
    alarm = group["alarm"]
    lines = [f'  {group["config"]} | {group["n"]} seed | {group["wall_seconds"]:.2f} s',
             f'    PDR {metric(group["pdr"])} | GW/GEN {group["received"]}/{group["gen"]}'
             f' | nhận trước 1000 s: {group["before_cutoff"]} | còn chờ: {group["pending"]}',
             f'    Trễ TB {metric(group["latency"], lambda x: f"{x:.3f} s")}'
             f' | năng lượng nút lớn nhất {metric(group["energy"]["0.4"], lambda x: f"{x:.2f}")}'
             ' giây TX tương đương (rho=0,4)',
             "    PDR nguồn " + "  ".join(
                 f'S{i} {pct(m["mean"]) if m else "NA"}' for i, m in group["nodes"].items())]
    if alarm:
        lower, upper = alarm["ci95"]
        reached = lower >= .90
        lines.append(f'    Cảnh báo ≤30 s: {alarm["success"]}/{alarm["n"]} '
                     f'({pct(alarm["success"] / alarm["n"])} | Wilson CI95% {pct(lower)} – {pct(upper)})'
                     f' | {"ĐẠT" if reached else "CHƯA CHỨNG MINH ĐẠT"}')
        lines.append(f'    PDR gói 255 {metric(group["alarm_pdr"])} | trễ cảnh báo của lượt nhận được '
                     f'{metric(group["alarm_delay"], lambda x: f"{x:.3f} s")}')
    if group["paired_pdr_delta"]:
        lines.append(f'    Δ PDR so với FULL {metric(group["paired_pdr_delta"], lambda x: f"{x*100:+.2f} đpt")}')
    return lines


def optimization_score(groups):
    alarms = [r for g in groups for r in g["runs"] if r["alarm_on_time"] is not None]
    rates = [mean(r["alarm_on_time"] for r in g["runs"]) for g in groups
             if g["runs"][0]["alarm_on_time"] is not None]
    energy = max(mean(weakest_energy(r) for r in g["runs"]) for g in groups)
    delays = sorted(r["alarm_delay"] for r in alarms if r["alarm_delay"] is not None)
    p95 = delays[math.ceil(.95 * len(delays)) - 1] if delays else math.inf
    tx = sum(radio["tx"] for g in groups for r in g["runs"] for radio in r["radio"].values())
    worst = min(rates)
    return (worst < .9, 0 if worst >= .9 else -worst, energy, p95, tx)


def optimize(folder, profile):
    base = Config(profile=profile)
    levels = dict(alarm_copies=(1, 2, 3, 5), jitter=((.1, .4), (.4, 1.0)),
                  l0=(2, 5), silence=(45, 90))
    stages = []
    baseline = [run_group(folder, i, base, range(1, 11), stage="screen") for i in (0, 3, 4, 6)]
    best = {}
    for field, options in levels.items():
        scores = []
        for index, value in enumerate(options):
            config = replace(base, name=f"{field}-{index}", **{field: value})
            groups = (baseline if value == getattr(base, field) else
                      [run_group(folder, i, config, range(1, 11), stage="screen")
                       for i in (0, 3, 4, 6)])
            scores.append((optimization_score(groups), index, value))
        best[field] = [row[2] for row in sorted(scores)[:2]]
    for index, values in enumerate(itertools.product(*best.values()), 1):
        config = replace(base, name=f"TUNED-{index:02}", **dict(zip(best, values)))
        groups = [run_group(folder, i, config, range(1, 31), stage="tune") for i in range(7)]
        stages.append((optimization_score(groups), config))
    stages.sort(key=lambda entry: entry[0])
    chosen = stages[0][1]
    confirmed = {}
    for scenario in range(7):
        group = run_group(folder, scenario, chosen, range(1001, 1031), stage="confirm-30")
        if scenario in ALARM_SCENARIOS:
            previous = 30
            for size in (60, 100, 200):
                successes = sum(r["alarm_on_time"] for r in group["runs"])
                if successes / previous < .90 or wilson(successes, previous)[0] >= .90:
                    break
                extra = run_group(folder, scenario, chosen, range(1001 + previous, 1001 + size),
                                  stage=f"confirm-{size}")
                group["runs"].extend(extra["runs"])
                group["wall_seconds"] += extra["wall_seconds"]
                previous = size
        confirmed[scenario] = group_summary(scenario, group)
    write_json(folder / "optimization.json", dict(
        selected=asdict(chosen), ranked=[dict(config=asdict(c), score=[
            None if isinstance(v, float) and not math.isfinite(v) else v for v in s])
            for s, c in stages], confirmation=confirmed))
    return chosen, confirmed


def worker(args):
    started = perf_counter()
    groups = [run_group(args.output, args.scenario, config, range(1, args.seeds + 1),
                        args.trace and config.name == "FULL")
              for config in configurations(args.scenario, args.profile, not args.full_only)]
    summaries = [group_summary(args.scenario, group, groups[0]["runs"]) for group in groups]
    with (args.output / f"KB-{args.scenario}.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("config", "seed", "pdr", "latency_s", "alarm_on_time", "alarm_delay_s",
                         "max_sensor_energy_rho_04", "wall_s"))
        for group in groups:
            for run in group["runs"]:
                writer.writerow((group["config"], run["seed"], run["network"]["pdr"],
                                 run["network"]["latency"], run["alarm_on_time"],
                                 run["alarm_delay"], weakest_energy(run), run["wall_seconds"]))
    write_json(args.output / f"KB-{args.scenario}.json",
               dict(groups=summaries, wall_seconds=perf_counter() - started))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", nargs="?", type=int, choices=range(7))
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--profile", choices=("LORA_STRESS", "LEGACY_IID"), default="LORA_STRESS")
    parser.add_argument("--full-only", action="store_true")
    parser.add_argument("--trace", action="store_true", help="Save per-event JSONL for FULL")
    parser.add_argument("--optimize", action="store_true", help="Run the additional V3 parameter sweep")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--output", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.seeds < 1 or (args.optimize and args.scenario is not None):
        parser.error("Use at least one seed and run optimization with all scenarios.")
    if args.worker:
        worker(args)
        return 0

    folder = ROOT / "results_v3" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    folder.mkdir(parents=True)
    scenarios = range(7) if args.scenario is None else [args.scenario]
    lines = ["MÔ PHỎNG LORA V3", f"Bộ mô phỏng sự kiện Python | {args.profile}",
             f"{args.seeds} seed/cấu hình | sinh gói {GEN_END} s | theo dõi đến {END} s",
             f"Hạn chạy mỗi kịch bản: 600 s trên máy | Chi tiết: {folder}"]
    failed = False
    started = perf_counter()
    for scenario in scenarios:
        cmd = [sys.executable, str(Path(__file__).resolve()), str(scenario), "--worker",
               "--output", str(folder), "--seeds", str(args.seeds), "--profile", args.profile]
        cmd.extend(flag for enabled, flag in ((args.full_only, "--full-only"),
                                             (args.trace, "--trace")) if enabled)
        title = f"KB-{scenario} | {NAMES[scenario]}"
        print(title, flush=True)
        try:
            tick = perf_counter()
            subprocess.run(cmd, check=True, timeout=600)
            result = json.loads((folder / f"KB-{scenario}.json").read_text(encoding="utf-8"))
            elapsed = perf_counter() - tick
            lines.extend(["", f"{title} | chạy máy {elapsed:.2f} s"])
            for group in result["groups"]:
                lines.extend(report_group(group))
            print(f"  Hoàn tất sau {elapsed:.2f} s", flush=True)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as error:
            failed = True
            reason = "vượt giới hạn 600 s" if isinstance(error, subprocess.TimeoutExpired) else str(error)
            lines.extend(["", f"{title} | LỖI: {reason}"])
            print(f"  LỖI: {reason}", flush=True)
    if args.optimize and not failed:
        print("Đang quét tham số bổ sung và xác nhận độc lập", flush=True)
        chosen, confirmed = optimize(folder, args.profile)
        lines.extend(["", f"Cấu hình chọn từ quét: {asdict(chosen)}"])
        for scenario, summary in confirmed.items():
            lines.append(f"Xác nhận độc lập KB-{scenario}")
            lines.extend(report_group(json.loads(json.dumps(summary))))
    lines.extend(["", f"Tổng thời gian chạy máy: {perf_counter() - started:.2f} s"])
    report = "\n".join(lines) + "\n"
    path = ROOT / "log.txt"
    if path.exists():
        shutil.copy2(path, folder / "previous_log.txt")
    write_path = folder / "log.txt"
    write_path.write_text(report, encoding="utf-8")
    staging = folder / "publish-log.txt"
    shutil.copy2(write_path, staging)
    staging.replace(path)
    print(f"Đã ghi kết quả: {path}", flush=True)
    return int(failed)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
