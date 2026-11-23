"""Rebuild the paper's seed-level dataset and summaries from the two V3 batches."""
import csv
import json
import math
import sys
from pathlib import Path
from statistics import mean, stdev

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from run_v3 import MODEL_HASH, configurations, wilson


def summarize():
    groups = {}
    rows = []
    for scenario in range(7):
        for cfg in configurations(scenario, 'LORA_STRESS', True):
            group = []
            for seed in range(1, 36):
                batch = HERE if seed > 30 else HERE.parent / '20261120-003100-010879'
                folder = batch / 'benchmark' / f'KB-{scenario}' / cfg.name / f'seed-{seed}'
                manifest = json.loads((folder / 'manifest.json').read_text())
                run = json.loads((folder / 'metrics.json').read_text())
                assert manifest['model_sha256'] == MODEL_HASH
                assert manifest['config'] == json.loads(json.dumps(vars(cfg)))
                assert manifest['scenario'] == scenario and manifest['seed'] == run['seed'] == seed
                energy = max(run['radio'][str(i)]['energy']['0.4'] for i in range(1, 11))
                row = dict(scenario=scenario, config=cfg.name, seed=seed,
                           on_time=run['alarm_on_time'], pdr=run['network']['pdr'], energy=energy)
                rows.append(row)
                group.append(row)
            groups[scenario, cfg.name] = group
    assert len(groups) == 35 and len(rows) == 1225
    with (HERE / 'paired_seeds.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    tables = {}
    for (scenario, name), group in groups.items():
        count = sum(r['on_time'] for r in group) if scenario in (3, 4, 6) else None
        tables[f'{scenario}/{name}'] = dict(count=count, energy=mean(r['energy'] for r in group),
            pdr=100*mean(r['pdr'] for r in group), wilson=wilson(count, 35) if count is not None else None)
    diffs = [100*(a['pdr']-b['pdr']) for a,b in zip(groups[5,'FULL'], groups[5,'NO_BYPASS'])]
    delta = mean(diffs)
    half = 2.0322445093 * stdev(diffs) / math.sqrt(35)
    result = dict(groups=tables, kb5_paired_t=dict(mean=delta, ci95=[delta-half, delta+half]))
    (HERE / 'paper_tables.json').write_text(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    summarize()
