import csv
import json
from pathlib import Path
import numpy as np
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run_experiment import OUT, configs, save

def wilson(k,n=50):
    z=1.959963984540054; p=k/n; d=1+z*z/n
    mid=(p+z*z/(2*n))/d
    h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,float(mid-h)),min(1,float(mid+h))]

def paired(a,b,binary=False):
    d=np.asarray(a,dtype=float)-np.asarray(b,dtype=float)
    if binary:
        rng=np.random.default_rng(20261124)
        samples=d[rng.integers(0,len(d),size=(20000,len(d)))].mean(axis=1)
        ci=np.quantile(samples,[.025,.975]); method='paired percentile bootstrap, 20000 resamples'
    else:
        h=t.ppf(.975,len(d)-1)*d.std(ddof=1)/np.sqrt(len(d))
        ci=[d.mean()-h,d.mean()+h]; method='paired t, df=49'
    out=dict(mean=float(d.mean()),ci95=list(map(float,ci)),method=method)
    if binary:
        out.update(full_only=int(sum((np.array(a)==1)&(np.array(b)==0))),
                   other_only=int(sum((np.array(a)==0)&(np.array(b)==1))))
    return out

def main():
    assert json.loads((OUT/'completion.json').read_text())['completed']==2450
    groups={};rows=[];by_node=[]
    for sc in range(7):
        for cfg in configs(sc):
            group=[]
            for seed in range(1,51):
                p=OUT/'benchmark'/f'SC-{sc}'/cfg.name/f'seed-{seed}'/'metrics.json'
                r=json.loads(p.read_text())
                radios=[r['radio'][str(i)] for i in range(1,11)]
                row=dict(scenario=sc,config=cfg.name,seed=seed,on_time=r['alarm_on_time'],
                    pdr=100*r['network']['pdr'],energy=max(x['energy']['0.4'] for x in radios),
                    tx_max=max(x['tx'] for x in radios),alarm_delay=r['alarm_delay'],
                    latency=r['network']['latency'],gen=r['network']['gen'],received=r['network']['received'])
                group.append(row);rows.append(row)
                for node in range(1,11):
                    by_node.append(dict(scenario=sc,config=cfg.name,seed=seed,node=node,**r['nodes'][str(node)]))
            groups[f'{sc}/{cfg.name}']=group
    assert len(rows)==2450 and len(groups)==49
    for filename, data in [('paired_results.csv',rows),('per_node.csv',by_node)]:
        with (OUT/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    summary={}
    for key,g in groups.items():
        k=sum(x['on_time'] for x in g) if g[0]['on_time'] is not None else None
        summary[key]=dict(n=50,count=k,wilson=wilson(k) if k is not None else None,
            **{m:float(np.mean([x[m] for x in g])) for m in ('pdr','energy','tx_max')},
            no_alarm=sum(x['alarm_delay'] is None for x in g) if k is not None else None)
    comparisons={}
    for key,g in groups.items():
        sc,name=key.split('/')
        if name=='FULL':continue
        full=groups[f'{sc}/FULL']; c={}
        for metric in ('pdr','energy','tx_max'):
            c[metric]=paired([r[metric] for r in full],[r[metric] for r in g])
        if g[0]['on_time'] is not None:
            c['on_time']=paired([r['on_time'] for r in full],[r['on_time'] for r in g],True)
        comparisons[key]=c
    save(OUT/'paper_tables.json',dict(groups=summary,comparisons=comparisons))
    figures=OUT/'figures';figures.mkdir(exist_ok=True)
    names=['BASE_5','BASE_30','FULL','FIXED_5','FIXED_30','NO_REPEAT','NO_ESCALATE','NO_BYPASS','ORACLE_BYPASS']
    fig,axes=plt.subplots(1,3,figsize=(10,4.5),sharey=True)
    for ax,sc in zip(axes,(3,4,6)):
        for y,name in enumerate(names):
            g=summary.get(f'{sc}/{name}')
            if not g:continue
            val=g['count']*2;lo,hi=np.array(g['wilson'])*100
            ax.errorbar(val,y,xerr=[[max(0,val-lo)],[max(0,hi-val)]],fmt='o',capsize=3,color='#b24c21' if name.startswith('BASE') else '#226b92')
            ax.annotate(f"{g['count']}/50",(val,y),xytext=(0,7),textcoords='offset points',fontsize=8,ha='center')
        ax.axvline(90,color='gray',linestyle='--',linewidth=1)
        ax.set_xlim(-5,111);ax.set_title(f'SC-{sc}');ax.set_xlabel('On-time alerts (%)');ax.grid(axis='x',alpha=.2)
    axes[0].set_yticks(range(len(names)),names,fontsize=9);axes[0].set_ylim(len(names)-.5,-.7)
    fig.tight_layout();fig.savefig(figures/'fig4.png',dpi=300);fig.savefig(figures/'fig4.pdf');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9,3.4))
    for name in ('BASE_5','BASE_30','FULL'):
        for ax,metric in zip(axes,('pdr','energy')):
            ax.plot(range(7),[summary[f'{sc}/{name}'][metric] for sc in range(7)],marker='o',label=name)
    for ax,label in zip(axes,('Mean data PDR (%)','Mean maximum radio load (TX-equiv. s)')):
        ax.set_xticks(range(7),[f'SC-{s}' for s in range(7)]);ax.set_ylabel(label);ax.grid(alpha=.2);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(figures/'baseline_comparison.png',dpi=300);fig.savefig(figures/'baseline_comparison.pdf');plt.close(fig)
    print(json.dumps({k:v for k,v in summary.items() if k.startswith(('3/','4/','5/','6/'))},indent=2))

if __name__=='__main__':main()
