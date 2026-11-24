"""Frozen 50-seed experiment; run without optimization or optional stopping."""
import csv
import hashlib
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path
from time import perf_counter
from collections import Counter
from simulation_v3 import Config, Simulation, Packet, AIRTIME, downstream

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'results'

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def configs(sc):
    full = Config()
    out = [full, replace(full, name='FIXED_5', fixed=5),
           replace(full, name='FIXED_30', fixed=30), replace(full, name='NO_REPEAT', repeat=False)]
    if sc in (3,4,6):
        out.append(replace(full, name='NO_ESCALATE', escalate=False))
    if sc in (5,6):
        out.extend([replace(full, name='NO_BYPASS', bypass=False), replace(full, name='ORACLE_BYPASS', oracle=True)])
    for period in (5,30):
        out.append(replace(full, name=f'BASE_{period}', fixed=period, repeat=False,
                           escalate=False, bypass=False, detect=False))
    return out

def pilot():
    checks = []
    started = perf_counter()
    for sc in range(7):
        for cfg in [c for c in configs(sc) if c.name in ('FULL','BASE_5','BASE_30')]:
            for seed in (1,2):
                events=[]
                sim=Simulation(sc,seed,cfg,events.append)
                result=sim.run()
                folder=OUT/'pilot'/f'SC-{sc}'/cfg.name/f'seed-{seed}'
                folder.mkdir(parents=True,exist_ok=True)
                with (folder/'events.jsonl').open('w',encoding='utf-8') as stream:
                    for e in events: stream.write(json.dumps(e)+'\n')
                if cfg.name.startswith('BASE'):
                    assert all(e.get('flag') not in (150,200) for e in events)
                    assert all(e['event'] not in ('DETECT','REPAIR_TX','BYPASS_ON','REVERT') for e in events)
                    assert all(e['period']==cfg.fixed for e in events if e['event']=='LEVEL')
                    starts=[e for e in events if e['event']=='TX_START']
                    assert all(e['to']==downstream(e['node']) for e in starts)
                    counts=Counter((e['node'],e['src'],e['seq']) for e in starts)
                    assert max(counts.values(), default=0)<=1
                    assert all(st.hop==downstream(n) for n,st in sim.nodes.items() if n!=11)
                    if sc==5:
                        assert not any(p.gen>=90 and p.src>=3 and p.key in sim.delivered for p in sim.generated.values())
                    assert all(p.flag in (0,100,255) for p in sim.generated.values())
                checks.append(dict(scenario=sc,config=cfg.name,seed=seed,passed=True))
    # A success exactly on the deadline is included; missing delivery is not zero delay.
    sim=Simulation(3,1,Config())
    p=Packet(5,1,255,90,73)
    sim.generated[p.key]=p
    sim.delivered[p.key]=103
    assert sim.summary()['alarm_on_time'] is True
    sim.delivered.clear()
    assert sim.summary()['alarm_on_time'] is False and sim.summary()['alarm_delay'] is None
    save(OUT/'pilot_checks.json',dict(checks=checks,wall_seconds=perf_counter()-started,
         deadline_boundary=True,missing_delivery=True))
    print(f'PILOT PASS: {len(checks)} runs, {perf_counter()-started:.2f}s',flush=True)

def main():
    if (OUT/'completion.json').exists():
        raise SystemExit('Completed output exists; use a new experiment directory to rerun.')
    pilot()
    model_hash=hashlib.sha256((HERE/'simulation_v3.py').read_bytes()).hexdigest()
    old_hash=hashlib.sha256((ROOT/'simulation_v3.py').read_bytes()).hexdigest()
    runner_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    save(OUT/'design.json',dict(seeds=list(range(1,51)),pairs=49,runs=2450,
         model_sha256=model_hash,original_model_sha256=old_hash,runner_sha256=runner_hash,
         frequency_mhz=920,frequency_note='Nominal metadata only; carrier frequency is not an input to propagation or airtime.',
         old_frequency_mhz=868,activity_end=1000,simulation_end=1300,python=sys.version,
         predeclared_stop=50,analysis='exploratory; extension after inspecting 30 and 35 seeds'))
    started=perf_counter(); completed=0; matched=0
    for sc in range(7):
        for cfg in configs(sc):
            group_start=perf_counter()
            for seed in range(1,51):
                tick=perf_counter()
                result=Simulation(sc,seed,cfg).run()
                # Normalize JSON key types before comparing exactly with saved legacy outputs.
                result=json.loads(json.dumps(result))
                if not cfg.name.startswith('BASE') and seed<=35:
                    batch='extension_35' if seed>30 else '20261120-003100-010879'
                    old_folder=ROOT/'results_v3'/batch/'benchmark'/f'KB-{sc}'/cfg.name/f'seed-{seed}'
                    old=json.loads((old_folder/'metrics.json').read_text(encoding='utf-8'))
                    old.pop('wall_seconds',None)
                    manifest=json.loads((old_folder/'manifest.json').read_text(encoding='utf-8'))
                    assert manifest['model_sha256']==old_hash
                    assert result==old, f'Regression mismatch SC-{sc}/{cfg.name}/{seed}'
                    matched+=1
                folder=OUT/'benchmark'/f'SC-{sc}'/cfg.name/f'seed-{seed}'
                result['wall_seconds']=perf_counter()-tick
                save(folder/'metrics.json',result)
                save(folder/'manifest.json',dict(scenario=sc,seed=seed,config=asdict(cfg),model_sha256=model_hash,
                     runner_sha256=runner_hash,frequency_mhz=920,frequency_role='metadata only',airtime=AIRTIME,
                     activity_end=1000,simulation_end=1300))
                completed+=1
            progress=dict(completed=completed,total=2450,regression_matched=matched,
                scenario=sc,config=cfg.name,wall_seconds=perf_counter()-started,
                group_seconds=perf_counter()-group_start)
            save(OUT/'progress.json',progress)
            print(json.dumps(progress),flush=True)
    assert completed==2450 and matched==1225
    save(OUT/'completion.json',dict(completed=completed,old_observations_exactly_matched=matched,
         wall_seconds=perf_counter()-started,unique_observations=2450,pilot_runs=42))

if __name__=='__main__': main()
