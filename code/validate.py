import pandas as pd, numpy as np
r=pd.read_pickle('work/res.pkl'); o=r[r.odak].copy()
tests=o['Test Adı'].unique()
df=pd.read_pickle('work/val_raw.pkl')
df=df[df['Cihaz Adı'].isin(['Alinity1','Alinity2'])&df['Onay Durumu'].notna()]
df['x']=pd.to_numeric(df['Kontrol Sonucu'].str.replace(',','.',regex=False),errors='coerce'); df=df[df.x.notna()]
df['Tarih']=pd.to_datetime(df['Tarih'],format='mixed'); df['Test Adı']=df['Test Adı'].str.strip()
df=df[(df['Kontrol Kodu']==df['Lot'])&(df.Tarih>'2026-07-07 23:59:59')&df['Test Adı'].isin(tests)]
def mat(c):
    c=str(c)
    if c.startswith('8977'): return 'Bio-Rad chem'
    if c.startswith('4048'): return 'Bio-Rad IA'
    if c.startswith('0158') or c.startswith('0153'): return 'Technopath chem'
    if c.startswith('0352') or c.startswith('0347'): return 'Technopath IA'
    return 'other'
df['mat']=df['Kontrol Kodu'].map(mat)
g=df.groupby(['Test Adı','Cihaz Adı','Seviye','Kontrol Kodu','mat'])
v=g.agg(n=('x','size'),ilk=('Tarih','min'),son=('Tarih','max'),ort=('x','mean'),sd=('x','std')).reset_index()
v['CV']=v.sd/v.ort*100; v['gun']=(v.son-v.ilk).dt.days
v.to_pickle('work/val_units.pkl')
print(v.groupby('mat').agg(units=('n','size'),n_med=('n','median'),gun_med=('gun','median'),lots=('Kontrol Kodu',lambda s: sorted(s.unique()))).to_string())
