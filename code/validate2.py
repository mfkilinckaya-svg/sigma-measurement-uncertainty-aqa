import pandas as pd, numpy as np
r=pd.read_pickle('work/res.pkl'); o=r[r.odak].copy()
v=pd.read_pickle('work/val_units.pkl')
ms=pd.read_pickle('work/mc_cvisabit.pkl').rename(columns={'test':'Test Adı','cihaz':'Cihaz Adı','lot':'Kontrol Kodu'})
mm=pd.read_pickle('work/mc.pkl').rename(columns={'test':'Test Adı','cihaz':'Cihaz Adı','lot':'Kontrol Kodu'})
o=o.merge(ms[['Test Adı','Cihaz Adı','Kontrol Kodu','OC_Psinif','klasik_Psinif','TR_Psinif']].rename(columns=lambda c: c+'_fix' if c.endswith('Psinif') else c),on=['Test Adı','Cihaz Adı','Kontrol Kodu'],how='left')
o=o.merge(mm[['Test Adı','Cihaz Adı','Kontrol Kodu','OC_Psinif','klasik_Psinif','TR_Psinif','OC_alt','OC_ust']],on=['Test Adı','Cihaz Adı','Kontrol Kodu'],how='left')
bands=[3,4,5,6]; cls=lambda x: np.digitize(x,bands)
def compare(vsel, label, same_lot):
    key=['Test Adı','Cihaz Adı','Seviye']+(['Kontrol Kodu'] if same_lot else [])
    m=o.merge(vsel,on=key,suffixes=('','_v'))
    m=m[(m.n_v>=40)&(m.gun_v>=45)]
    m['s_OC_v']=m.CVI/m.CV_v; m['s_kl_v']=m.TEa_BV/m.CV_v; m['s_TR_v']=m.TEa_TR/m.CV_v
    out={'label':label,'units':len(m),'measurands':m['Test Adı'].nunique(),'n_med':m.n_v.median(),'days_med':m.gun_v.median(),
         'CVratio_med':(m.CV_v/m.CV).median().round(2),'CVratio_range':(round((m.CV_v/m.CV).min(),2),round((m.CV_v/m.CV).max(),2))}
    for s,sv,P in [('s_OC','s_OC_v','OC_Psinif_fix'),('s_klasik','s_kl_v','klasik_Psinif_fix'),('s_TR','s_TR_v','TR_Psinif_fix')]:
        d=m.dropna(subset=[s,sv]); same=cls(d[s])==cls(d[sv])
        out[s+'_same']=f'{same.sum()}/{len(d)}'
        for nm,mask in [('cert',d[P]>=0.95),('mid',(d[P]>=0.80)&(d[P]<0.95)),('unc',d[P]<0.80)]:
            out[f'{s}_{nm}']=f'{same[mask].sum()}/{mask.sum()}'
        out[s+'_up']=int((cls(d[sv])>cls(d[s])).sum()); out[s+'_down']=int((cls(d[sv])<cls(d[s])).sum())
    d=m.dropna(subset=['OC_alt']); out['OC_in_MCint']=f"{((d.s_OC_v>=d.OC_alt)&(d.s_OC_v<=d.OC_ust)).sum()}/{len(d)}"
    m.to_pickle(f'work/val_{label}.pkl'); return out
v_chem=v[v.mat=='Bio-Rad chem']
v_ia=v[(v.mat=='Technopath IA')&v['Kontrol Kodu'].str.startswith('0352')]
res=[compare(v_chem,'temporal_chem',True), compare(v_ia,'newlot_IA',False)]
print(pd.DataFrame(res).T.to_string())
