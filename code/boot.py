import pandas as pd,numpy as np
rng=np.random.default_rng(7); B=4000
r=pd.read_pickle('work/res.pkl'); a=r[r.odak].copy(); a['m']=a['Test Adı'].replace({'Glukoz Açlık':'GLUKOZ, AÇLIK'})
cols={'O–C':'s_OC','BV':'s_klasik','CLIA':'s_CLIA','RiliBÄK':'s_Rili','Directive':'s_TR'}
ms=a.m.unique(); groups={k:a[a.m==k] for k in ms}
res={k:[] for k in cols}
for b in range(B):
    s=pd.concat([groups[k] for k in rng.choice(ms,len(ms))])
    for k,c in cols.items():
        v=s[c].dropna(); res[k].append((v<3).mean()*100 if len(v) else np.nan)
for k,c in cols.items():
    v=a[c].dropna(); lo,hi=np.nanpercentile(res[k],[2.5,97.5]); print(f'{k}: {(v<3).mean()*100:.0f}% ({lo:.0f}–{hi:.0f})')
o=pd.read_pickle('work/calib.pkl'); tests=o.test.unique(); og={t:o[o.test==t] for t in tests}
rr={g:[] for g in ['cert','mid','unc']}
for b in range(B):
    s=pd.concat([og[t] for t in rng.choice(tests,len(tests))])
    for g in rr: v=s[s.grp==g].obs; rr[g].append(v.mean()*100 if len(v) else np.nan)
for g in rr:
    v=o[o.grp==g].obs; lo,hi=np.nanpercentile(rr[g],[2.5,97.5]); print(g, f'{v.mean()*100:.0f}% ({lo:.0f}–{hi:.0f})')
