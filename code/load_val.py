import pandas as pd, sys
f=sys.argv[1]
df=pd.read_excel(f,sheet_name=0,dtype=str,usecols=['Tarih','Cihaz Adı','Seviye','Kontrol Kodu','Lot','Test Adı','Kontrol Sonucu','Birimi','Onay Durumu'])
df.to_pickle('work/val_raw.pkl')  # personel sütunları okunmadı; Sheet2 okunmadı
print(len(df))
