import pandas as pd, numpy as np, sys
RAW, STATS, OUT = sys.argv[1:4]
# ---------- IQC ----------
keep=['Tarih','Cihaz Adı','Seviye','Kontrol Kodu','Lot','Test Adı','Kontrol Sonucu','Birimi','Onay Durumu']
df=pd.read_excel(RAW,sheet_name=0,dtype=str,usecols=keep)   # staff columns are never read
df=df[df['Cihaz Adı'].isin(['Alinity1','Alinity2'])]
n0=len(df)
df=df[df['Onay Durumu'].notna()]          # onaysız kayıtlar dışlanır
n_unapproved=n0-len(df)
df['x']=pd.to_numeric(df['Kontrol Sonucu'].str.replace(',','.',regex=False),errors='coerce')
df=df[df['x'].notna()]
df['Tarih']=pd.to_datetime(df['Tarih'],format='mixed')
n_mis=int((df['Kontrol Kodu']!=df['Lot']).sum())
df=df[df['Kontrol Kodu']==df['Lot']]   # kod-lot uyuşmazlığı dışlanır
df['Test Adı']=df['Test Adı'].str.strip()
# provisional EFLM table
e=pd.read_excel(STATS,sheet_name='EFLM_BV_Kaynak',header=3)
e.columns=['test','CVI','CVG','a','b','c','durum']; e['test']=e['test'].str.strip()
e=e[['test','CVI','CVG']].dropna(); e['cvi_kaynak']='geçici (ikincil 2021)'
ef=pd.read_csv('data/eflm_bvd.csv',sep=';'); ef['cvi_kaynak']='EFLM BVD (ekran, '+ef['guncelleme']+')'
e=pd.concat([ef[['test','CVI','CVG','CVI_lo','CVI_hi','CVG_lo','CVG_hi','cvi_kaynak']],e[~e.test.isin(ef.test)]],ignore_index=True)
excl_kw=['İDRAR','BOS','idrar','hemoliz','DEMİR\b']
def is_serum(t): return not any(k in t for k in ['İDRAR','BOS','idrar','hemoliz'])
df=df[df['Test Adı'].apply(is_serum)]
def robust_flag(s):
    med=s.median(); mad=1.4826*(s-med).abs().median()
    return (s-med).abs()>4*mad if mad>0 else pd.Series(False,index=s.index)
df['out4']=df.groupby(['Test Adı','Cihaz Adı','Kontrol Kodu'])['x'].transform(lambda s: robust_flag(s))
g=df.groupby(['Test Adı','Cihaz Adı','Seviye','Kontrol Kodu','Birimi'])
res=g.agg(gun_sayisi=('Tarih',lambda t: t.dt.date.nunique()),n=('x','size'),ilk=('Tarih','min'),son=('Tarih','max'),ort=('x','mean'),sd=('x','std')).reset_index()
res['CV']=res['sd']/res['ort']*100
g2=df[~df['out4']].groupby(['Test Adı','Cihaz Adı','Seviye','Kontrol Kodu','Birimi'])['x']
r2=g2.agg(['size','mean','std']).reset_index().rename(columns={'size':'n_rob','mean':'ort_rob','std':'sd_rob'})
res=res.merge(r2,on=['Test Adı','Cihaz Adı','Seviye','Kontrol Kodu','Birimi'],how='left')
res['CV_rob']=res['sd_rob']/res['ort_rob']*100
res['gun']=(res['son']-res['ilk']).dt.days
res=res.merge(e,left_on='Test Adı',right_on='test',how='left').drop(columns='test')
# Bias is not included (no EQA data); classical sigma = TEa/CV_A
# ---------- sigma ----------
res['TEa_BV']=0.25*np.sqrt(res.CVI**2+res.CVG**2)+1.65*0.5*res.CVI
res['s_klasik']=res.TEa_BV/res.CV
res['s_OC']=res.CVI/res.CV
res['NDC']=1.41*res.CVI/res.CV
res['s_OC_rob']=res.CVI/res.CV_rob
y=pd.read_csv('data/yonerge_tablo1.csv',sep=';')
res=res.merge(y[['test','ikk_cv_max','dkd_pct','dkd_abs']].rename(columns={'test':'Test Adı'}),on='Test Adı',how='left')
conv=np.where(res['Test Adı']=='TESTOSTERON, TOTAL',0.01,1.0)   # ng/dL -> ng/mL
res['dkd_abs_iku']=res.dkd_abs*conv
res['TEa_TR']=np.where(res.dkd_abs.notna(),np.maximum(res.dkd_pct,res.dkd_abs*conv/res.ort*100),res.dkd_pct)
res['s_TR']=res.TEa_TR/res.CV
bands=[-np.inf,3,4,5,6,np.inf]; labs=['<3','3–4','4–5','5–6','≥6']
for c in ['s_klasik','s_OC','s_TR']:
    res['sinif_'+c]=pd.cut(res[c],bands,labels=labs,right=False).astype(str).replace('nan','')
def mat(k):
    if k.startswith('8') and not k.startswith('81'): return 'Bio-Rad'
    if k.startswith(('0347','0153','0140','0135','S13')): return 'Technopath'
    return 'diğer/bilinmiyor'
res['materyal']=res['Kontrol Kodu'].apply(mat)
res['ana_set']=(res.gun>=150)&(res.n>=100)&res.CVI.notna()&res.materyal.isin(['Bio-Rad','Technopath'])
odak={'SODYUM (Na), SERUM','POTASYUM (K), SERUM','KALSİYUM (Ca), TOTAL, SERUM','MAGNEZYUM (Mg), SERUM','GLUKOZ, AÇLIK','Glukoz Açlık',
'KREATİNİN, SERUM#','ÜRE, SERUM','ÜRİK ASİT, SERUM','SGPT (ALT)','SGOT (AST)','GGT (G-GLUTAMİL TRANSFERAZ)','ALP (ALKALEN FOSFATAZ)',
'KOLESTEROL, TOTAL','KOLESTEROL, HDL','TRİGLİSERİDLER','ALBUMİN, SERUM','PROTEİN, TOTAL, SERUM',
'TSH','T4, SERBEST','T3, SERBEST','FERRİTİN','E2 (ESTRADİOL)','TESTOSTERON, TOTAL','KORTİZOL, SABAH','PRL (PROLAKTİN)','FSH (FOLİKÜL STİMÜNAL HORMON)','LH (LUTEİNİZAN HORMON)','PSA, TOTAL','AFP (ALFA-FETOPROTEİN)'}
res['odak']=res.ana_set & res['Test Adı'].isin(odak)
rg=pd.read_csv('data/regulatory.csv',sep=';').rename(columns={'test':'Test Adı'})
res=res.merge(rg,on='Test Adı',how='left')
def tea(pct,ab,mean):
    p=np.where(pd.notna(pct)&(pct>0),pct,np.nan); a=np.where(pd.notna(ab),ab/mean*100,np.nan)
    return np.fmax(p,a)
res['TEa_CLIA']=tea(res.clia_pct,res.clia_abs,res.ort)
inr=(res.ort>=res.rili_lo)&(res.ort<=res.rili_hi)
res['TEa_Rili']=np.where(inr,res.rili_eqa,np.nan)
res['s_CLIA']=res.TEa_CLIA/res.CV
res['s_Rili']=res.TEa_Rili/res.CV
for c in ['s_CLIA','s_Rili']:
    res['sinif_'+c]=pd.cut(res[c],bands,labels=labs,right=False).astype(str).replace('nan','')
res.to_pickle(OUT)
print('kod-lot uyuşmazlığı dışlanan:',n_mis); print('kayıt (Alinity):',n0,'onaysız dışlanan:',n_unapproved,'birim:',len(res),'ana set:',res.ana_set.sum(),
      '4·MAD dışlanan:',int(df.out4.sum()))
