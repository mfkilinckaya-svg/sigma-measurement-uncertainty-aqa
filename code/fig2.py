import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def proportion_confint(k,n,method='wilson',z=1.959964):
    p=k/n; d=1+z**2/n; c=(p+z**2/(2*n))/d; h=z*np.sqrt(p*(1-p)/n+z**2/(4*n**2))/d
    return c-h,c+h
groups=['Certain\n(P ≥ 0.95)','Intermediate\n(0.80–0.95)','Uncertain\n(P < 0.80)']
data={'Same lots, later period':[(106,130),(6,38),(10,36)],'New control lots':[(62,84),(7,28),(6,20)]}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
fig,ax=plt.subplots(figsize=(5.2,3.4),dpi=300)
x=np.arange(3); w=0.34; fills=['#3a3a3a','white']
import pandas as pd
c=pd.read_pickle('work/calib.pkl'); ex=c.groupby(['design','grp'],observed=True).exp.mean()
expd={'Same lots, later period':[ex[('temporal_chem',g)]*100 for g in ['cert','mid','unc']],'New control lots':[ex[('newlot_IA',g)]*100 for g in ['cert','mid','unc']]}
for i,(lab,vals) in enumerate(data.items()):
    k=np.array([v[0] for v in vals]); n=np.array([v[1] for v in vals]); p=k/n*100
    lo,hi=proportion_confint(k,n,method='wilson'); lo*=100; hi*=100
    xs=x+(i-0.5)*w
    ax.bar(xs,p,w*0.92,color=fills[i],edgecolor='black',linewidth=0.8,label=lab)
    ax.errorbar(xs,p,yerr=[p-lo,hi-p],fmt='none',ecolor='black',elinewidth=0.8,capsize=2.5)
    ax.plot(xs,expd[lab],'D',mfc='white',mec='black',ms=5,mew=1,zorder=5,label='Expected from sampling error alone' if i==1 else None)
    for xx,pp,kk,nn,h in zip(xs,p,k,n,hi):
        ax.text(xx,2.5,f'{kk}/{nn}',ha='center',va='bottom',fontsize=7,color='white' if i==0 else 'black')
ax.set_xticks(x); ax.set_xticklabels(groups)
ax.set_ylabel('Classes unchanged in validation (%)'); ax.set_ylim(0,110); ax.set_yticks(range(0,101,20))
ax.set_xlabel('Monte Carlo certainty of the class in the main period')
for s in ['top','right']: ax.spines[s].set_visible(False)
ax.legend(frameon=False,loc='upper right',fontsize=8)
fig.tight_layout(); fig.savefig('out/Fig2_class_retention.png'); fig.savefig('out/Fig2_class_retention.pdf')
