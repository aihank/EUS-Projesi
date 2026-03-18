import pandas as pd
import sqlite3
import re
import os

# Global Değişken
EGITIM_OGRETIM_YILI = "2025-2026"

def veriyi_oku(dosya_yolu):
    # ŞART 1: Sahte Excel Koruması (Try-Except Bloğu)
    try:
        print(f"Deneniyor: read_excel -> {dosya_yolu}")
        df = pd.read_excel(dosya_yolu)
    except Exception:
        try:
            print("Deneniyor: read_html... (E-Okul Tuzağı Aşıldı!)")
            # read_html liste döndürür, en büyük tabloyu alalım
            dfs = pd.read_html(dosya_yolu, decimal=',', thousands='.')
            df = max(dfs, key=len)
        except Exception:
            print("Deneniyor: read_csv...")
            df = pd.read_csv(dosya_yolu, sep=None, engine='python')
    return df

def veritabani_islem(okul_no, donem_ek, mazeretsiz, mazeretli, toplam):
    conn = sqlite3.connect('okul_verisi.db')
    cursor = conn.cursor()
    
    # Foreign Key desteğini aktif edelim (İlişkisel yapı kullandığın için önemli)
    cursor.execute("PRAGMA foreign_keys = ON")

    # Dönem bilgisini birleştiriyoruz: "2025-2026 I. DÖNEM" gibi
    tam_donem = f"{EGITIM_OGRETIM_YILI} {donem_ek}"
    
    sorgu = """
    INSERT INTO devamsizlik (okul_no, donem, mazeretli, mazeretsiz, toplam) 
    VALUES (?, ?, ?, ?, ?)
    """
    
    try:
        cursor.execute(sorgu, (str(int(okul_no)), tam_donem, mazeretli, mazeretsiz, toplam))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        # Eğer ogrenciler tablosunda bu okul_no yoksa Foreign Key hatası verir
        print(f"Hata: Okul No {okul_no} sisteme kayıtlı değil! (Hayalet öğrenci elendi)")
        return False
    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return False
    finally:
        conn.close()

def rapor_isleme(dosya_yolu):
    df = veriyi_oku(dosya_yolu)
    # NaN değerleri boş string yapalım ki regex hata vermesin
    df = df.fillna('')
    
    mevcut_okul_no = None
    mevcut_donem = "GÜNCEL" # Varsayılan değer
    eklenen_kayit = 0
    
    for index, row in df.iterrows():
        satir_metni = " ".join(map(str, row.values))
        
        # 1. DÖNEM BİLGİSİNİ YAKALA
        # Satırda "1. Dönem" veya "I. Dönem" geçiyorsa hafızaya al
        if re.search(r'(1\.|I\.)\s?Dönem', satir_metni, re.IGNORECASE):
            mevcut_donem = "I. DÖNEM"
        elif re.search(r'(2\.|II\.)\s?Dönem', satir_metni, re.IGNORECASE):
            mevcut_donem = "II. DÖNEM"

        # 2. ÖĞRENCİ NUMARASINI YAKALA
        no_match = re.search(r'(?<!\d)(\d{1,4})(\.0)?(?!\d)', " ".join(map(str, row.values[:3])))
        if no_match:
            mevcut_okul_no = no_match.group(1)
            continue

        # 3. TOPLAMLAR SATIRINI YAKALA VE KAYDET
        if 'Toplamlar:' in satir_metni and mevcut_okul_no:
            sayilar = re.findall(r'\d+\.?\d*', satir_metni)
            float_sayilar = [float(s) for s in sayilar if '.' in s or s.isdigit()]
            
            if len(float_sayilar) >= 3:
                mazeretsiz = float_sayilar[0]
                mazeretli = float_sayilar[1]
                toplam = float_sayilar[2]
                
                # Veritabanına gönderirken yakaladığımız dönem bilgisini de veriyoruz
                basarili = veritabani_islem(mevcut_okul_no, mevcut_donem, mazeretsiz, mazeretli, toplam)
                if basarili:
                    eklenen_kayit += 1
                
                # Bir sonraki öğrenciye geçmeden önce numarayı sıfırla 
                mevcut_okul_no = None

    print(f"\n✅ ŞOV ZAMANI: Toplam {eklenen_kayit} öğrencinin devamsızlığı SQL'e başarıyla eklendi!")

# Çalıştır
if __name__ == "__main__":
    dosya = './d/devamsizlik.XLS'
    if os.path.exists(dosya):
        rapor_isleme(dosya)
    else:
        print(f"HATA: '{dosya}' bulunamadı! Lütfen aynı klasöre koyun.")