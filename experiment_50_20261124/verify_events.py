"""Targeted checks for event semantics and actual bypass delivery."""
import json
from simulation_v3 import Config, Simulation, Packet, Transmission, AIRTIME
from run_experiment import OUT, save

def main():
    # A later-arriving lower sequence is new in V3, but a repeat of it is discarded.
    sim=Simulation(0,1,Config())
    for seq in (2,1,1):
        packet=Packet(1,seq,0,0,0)
        sim.receive(Transmission(1,11,packet,str(seq),0,AIRTIME,set()))
    assert sim.nodes[11].seen=={(1,1),(1,2)} and len(sim.delivered)==2
    # Overlapping transmit and receive creates a half-duplex loss reason.
    sim=Simulation(0,1,Config())
    sim.enqueue(2,Packet(2,1,0,0,0))
    sim.enqueue(1,Packet(1,1,0,0,0))
    assert 'HALF_DUPLEX' in sim.active[2].reasons
    # Environment trajectories do not depend on query order at different transmission times.
    from simulation_v3 import Channel
    a=Channel(1,3,Config());b=Channel(1,3,Config())
    for time in range(131):
        av=a.lost(5,4,time,str(time))
        if time%10==0: assert av==b.lost(5,4,time,str(time))
    full=[json.loads(line) for line in (OUT/'pilot'/'SC-5'/'FULL'/'seed-1'/'events.jsonl').read_text().splitlines()]
    bypass=[e for e in full if e['event']=='RX_OK' and e.get('source')==4 and e.get('to')==2 and e.get('flag') in (0,100,255)]
    gw={(e['src'],e['seq']):e for e in full if e['event']=='GW'}
    confirmed=[(e,gw[(e['src'],e['seq'])]) for e in bypass if (e['src'],e['seq']) in gw]
    assert confirmed
    # An RX_OK between two sampling instants proves receive is not gated by sampling.
    base=[json.loads(line) for line in (OUT/'pilot'/'SC-0'/'BASE_30'/'seed-1'/'events.jsonl').read_text().splitlines()]
    sample_times={e['t'] for e in base if e['event']=='LEVEL' and e['node']==1}
    assert any(e['event']=='RX_OK' and e['node']==1 and e['t'] not in sample_times for e in base)
    save(OUT/'event_checks.json',dict(out_of_order_dedup=True,half_duplex=True,
         channel_common_times=True,receive_independent_of_sampling=True,
         bypass_delivery_example=dict(link=confirmed[0][0],gateway=confirmed[0][1])))
    print('PASS: dedup, half duplex, channel pairing, event timing, actual bypass delivery')

if __name__=='__main__': main()
