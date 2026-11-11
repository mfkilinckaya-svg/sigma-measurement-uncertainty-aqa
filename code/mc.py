import pandas as pd, numpy as np, sys
rng=np.random.default_rng(20261110); N=10000
DF=sys.argv[1] if len(sys.argv)>1 else 'n'; CVIFIX=(len(sys.argv)>2 and sys.argv[2]=='sabit'); OUTP=sys.argv[3] if len(sys.argv)>3 else 'work/mc.pkl'
r=pd.read_pickle('work/res.pkl'); o=r[r.odak].copy().reset_index(drop=True)
def split_lognorm(med,lo,hi,z):
    lo=np.maximum(lo,0.1); hi=np.maximum(hi,med)
    lm=np.log(med); sl=(lm-np.log(np.minimum(lo,med)))/1.96; sh=(np.log(hi)-lm)/1.96
    return np.exp(lm+np.where(z<0,z*sl,z*sh))
bands=np.array([3,4,5,6]); labs=np.array(['<3','3–4','4–5','5–6','≥6'])
def cls(x): return np.digitize(x,bands)
rows=[]
for i,u in o.iterrows():
    df=(u.n-1) if DF=='n' else (max(u.gun_sayisi-1,2) if DF=='gun' else max(round(u.gun/7)-1,2))
    cv=u.CV*np.sqrt(rng.chisquare(df,N)/df)
    cvi=np.full(N,u.CVI) if CVIFIX else split_lognorm(u.CVI,u.CVI_lo,u.CVI_hi,rng.standard_normal(N))
    cvg=np.full(N,u.CVG) if (CVIFIX and pd.notna(u.CVG)) else split_lognorm(u.CVG,u.CVG_lo,u.CVG_hi,rng.standard_normal(N)) if pd.notna(u.CVG) else np.full(N,np.nan)
    tea_bv=0.25*np.sqrt(cvi**2+cvg**2)+0.825*cvi
    sims={'OC':cvi/cv,'klasik':tea_bv/cv,'TR':u.TEa_TR/cv,'CLIA':u.TEa_CLIA/cv,'Rili':u.TEa_Rili/cv}
    pt={'OC':u.s_OC,'klasik':u.s_klasik,'TR':u.s_TR,'CLIA':u.s_CLIA,'Rili':u.s_Rili}
    row=dict(test=u['Test Adı'],cihaz=u['Cihaz Adı'],lot=u['Kontrol Kodu'],n=u.n)
    for m,s in sims.items():
        if np.all(np.isnan(s)) or pd.isna(pt[m]): continue
        c0=cls(np.array([pt[m]]))[0]; cs=cls(s)
        row[f'{m}_nokta']=pt[m]; row[f'{m}_alt']=np.nanpercentile(s,2.5); row[f'{m}_ust']=np.nanpercentile(s,97.5)
        row[f'{m}_Psinif']=(cs==c0).mean(); row[f'{m}_P3']=(s>=3).mean()
        if m=='OC': row['OC_P465']=(s>=4.65).mean()
    if pd.notna(pt['klasik']):
        row['P_OC_klasik_farkli']=(cls(sims['OC'])!=cls(sims['klasik'])).mean()
        row['nokta_farkli']=cls(np.array([pt['OC']]))[0]!=cls(np.array([pt['klasik']]))[0]
    if pd.notna(pt['TR']):
        row['P_OC_TR_farkli']=(cls(sims['OC'])!=cls(sims['TR'])).mean()
    rows.append(row)
m=pd.DataFrame(rows); m.to_pickle(OUTP)
print('birim',len(m))
for k in ['OC','klasik','CLIA','Rili','TR']:
    c=f'{k}_Psinif'; v=m[c].dropna()
    print(f"{k:7s} N={len(v):3d}  sınıf kesin (P≥0,95): {(v>=0.95).sum():3d}  belirsiz (P<0,80): {(v<0.80).sum():3d}  medyan P={v.median():.2f}")
d=m.dropna(subset=['P_OC_klasik_farkli'])
d=d.assign(nf=d.nokta_farkli.astype(bool)); print('O–C vs klasik: nokta tahminde farklı',int(d.nf.sum()),'/',len(d),'; bunlardan farkın P≥0,95 olduğu',int(((d.P_OC_klasik_farkli>=0.95)&d.nf).sum()))
e=m.dropna(subset=['P_OC_TR_farkli']); print('O–C vs Yönerge: farklı sınıf P≥0,95 olan',int((e.P_OC_TR_farkli>=0.95).sum()),'/',len(e))
x=m.groupby('test')[['OC_alt','OC_nokta','OC_ust','OC_Psinif']].median().sort_values('OC_Psinif').round(2)
print(x.head(10).to_string())
print('OC GA genişliği (üst/alt) en büyük:'); m['oran']=m.OC_ust/m.OC_alt; print(m.groupby('test').oran.median().sort_values(ascending=False).head(6).round(2).to_string())
