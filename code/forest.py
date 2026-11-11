import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
m=pd.read_pickle('work/mc.pkl'); r=pd.read_pickle('work/res.pkl')
m=m.merge(r[['Test Adı','Cihaz Adı','Kontrol Kodu','Seviye','materyal']].rename(columns={'Test Adı':'test','Cihaz Adı':'cihaz','Kontrol Kodu':'lot'}),on=['test','cihaz','lot'])
en={'SODYUM (Na), SERUM':'Sodium','POTASYUM (K), SERUM':'Potassium','KALSİYUM (Ca), TOTAL, SERUM':'Calcium','MAGNEZYUM (Mg), SERUM':'Magnesium',
'GLUKOZ, AÇLIK':'Glucose','Glukoz Açlık':'Glucose','KREATİNİN, SERUM#':'Creatinine','ÜRE, SERUM':'Urea','ÜRİK ASİT, SERUM':'Urate','SGPT (ALT)':'ALT','SGOT (AST)':'AST',
'GGT (G-GLUTAMİL TRANSFERAZ)':'GGT','ALP (ALKALEN FOSFATAZ)':'ALP','KOLESTEROL, TOTAL':'Cholesterol','KOLESTEROL, HDL':'HDL-C','TRİGLİSERİDLER':'Triglycerides',
'ALBUMİN, SERUM':'Albumin','PROTEİN, TOTAL, SERUM':'Total protein','TSH':'TSH','T4, SERBEST':'FT4','T3, SERBEST':'FT3','FERRİTİN':'Ferritin','E2 (ESTRADİOL)':'Estradiol',
'TESTOSTERON, TOTAL':'Testosterone','KORTİZOL, SABAH':'Cortisol','PRL (PROLAKTİN)':'Prolactin','FSH (FOLİKÜL STİMÜNAL HORMON)':'FSH','LH (LUTEİNİZAN HORMON)':'LH',
'PSA, TOTAL':'PSA','AFP (ALFA-FETOPROTEİN)':'AFP'}
m['ad']=m.test.map(en); m['etk']=m.ad+'  '+m.cihaz.str.replace('Alinity','A')+' '+m.Seviye.str.replace('Seviye','L')
m['grup']=m.materyal.map({'Bio-Rad':'Clinical chemistry (Bio-Rad)','Technopath':'Immunoassay (Technopath)'})
fig,axes=plt.subplots(1,2,figsize=(11,15),sharex=True)
for ax,(g,d) in zip(axes,m.groupby('grup')):
    d=d.sort_values(['ad','cihaz','Seviye'],ascending=[False,False,False]).reset_index(drop=True)
    y=np.arange(len(d))
    ax.hlines(y-0.15,d.OC_alt,d.OC_ust,color='black',lw=1)
    ax.plot(d.OC_nokta,y-0.15,'o',color='black',ms=5,label='O–C: CV_I/CV_A')
    t=d.dropna(subset=['TR_nokta'])
    ax.hlines(t.index+0.15,t.TR_alt,t.TR_ust,color='0.45',lw=1)
    ax.plot(t.TR_nokta,t.index+0.15,'s',mfc='white',mec='0.3',ms=5,label='Directive 2026: TEa/CV_A')
    for xv,ls in [(3,'-'),(4.65,'--'),(6,'-')]: ax.axvline(xv,color='0.6',lw=0.7,ls=ls)
    ax.set_yticks(y); ax.set_yticklabels(d.etk,fontsize=8); ax.set_ylim(-1,len(d))
    ax.set_xscale('log'); ax.set_xlim(0.1,100); ax.set_xticks([0.1,0.3,1,3,6,10,30,100]); ax.set_xticklabels(['0.1','0.3','1','3','6','10','30','100'],fontsize=9)
    ax.set_title(('(a) ' if 'chem' in g else '(b) ')+g,fontsize=10,loc='left'); ax.set_xlabel('Sigma (log scale); bars = 95 % Monte Carlo interval',fontsize=9)
    for s in ['top','right']: ax.spines[s].set_visible(False)
h,l=axes[0].get_legend_handles_labels(); fig.legend(h,l,loc='upper center',ncol=2,fontsize=10,frameon=False)
plt.tight_layout(rect=(0,0,1,0.975))
plt.savefig('out/Fig_forest_sigma_MC.png',dpi=200); plt.savefig('out/Fig_forest_sigma_MC.pdf')
print('ok',len(m))
