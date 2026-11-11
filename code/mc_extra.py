import pandas as pd, numpy as np
rng=np.random.default_rng(20261111); N=20000
cls=lambda x: np.digitize(x,[3,4,5,6])
out=[]
for lab in ['temporal_chem','newlot_IA']:
    m=pd.read_pickle(f'work/val_{lab}.pkl').copy()
    # Directive TEa recomputed at validation mean (absolute component)
    m['TEa_TR_v']=np.where(m.dkd_abs_iku.notna(), np.fmax(m.dkd_pct, m.dkd_abs_iku/m.ort_v*100), m.dkd_pct)
    m['s_TR_v']=m.TEa_TR_v/m.CV_v
    for i,u in m.iterrows():
        n1=u.n-1; n2=u.n_v-1
        cvt=u.CV*np.sqrt(n1/rng.chisquare(n1,N)); cvn=cvt*np.sqrt(rng.chisquare(n2,N)/n2)
        for mod,T,pt,sv,P in [('OC',u.CVI,u.s_OC,u.CVI/u.CV_v,u.OC_Psinif_fix),
                              ('BV',u.TEa_BV,u.s_klasik,u.TEa_BV/u.CV_v,u.klasik_Psinif_fix),
                              ('TR',u.TEa_TR,u.s_TR,u.s_TR_v,u.TR_Psinif_fix)]:
            if pd.isna(T) or pd.isna(pt) or pd.isna(sv) or pd.isna(P): continue
            exp=(cls(T/cvn)==cls(pt)).mean()
            out.append(dict(design=lab,model=mod,test=u['Test Adı'],P=P,obs=int(cls(sv)==cls(pt)),exp=exp))
o=pd.DataFrame(out); o['grp']=pd.cut(o.P,[-1,0.8,0.95,2],right=False,labels=['unc','mid','cert'])
o.to_pickle('work/calib.pkl')
g=o.groupby(['design','grp'],observed=True).agg(n=('obs','size'),obs=('obs','mean'),exp=('exp','mean'))
print(g.round(3)); print(o.groupby('grp',observed=True).agg(n=('obs','size'),obs=('obs','mean'),exp=('exp','mean')).round(3))
print(o.groupby(['design','model']).obs.agg(['sum','size']))
