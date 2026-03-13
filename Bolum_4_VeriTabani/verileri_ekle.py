import sqlite3
import pdfplumber
import pandas as pd
import glob
import os
import re

def eokul_pdf_parser_smart(klasor_yolu):
    tum_veriler = []
    pdf_dosyalari = glob.glob(os.path.join(klasor_yolu, "*.pdf"))
    
    islenen_dersler_listesi = set()

    # Tablo çizgilerini baz alan hassas ayar
    tablo_ayarlari = {
        "vertical_strategy": "lines", 
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
    }

    print(f"{len(pdf_dosyalari)} dosya bulundu. Tüm notlar hücre hücre okunuyor...\n")

    for dosya_yolu in pdf_dosyalari:
        with pdfplumber.open(dosya_yolu) as pdf:
            for i, sayfa in enumerate(pdf.pages):
                text = sayfa.extract_text() or ""
                
                # --- YENİ: DÖNEM BİLGİSİNİ OTOMATİK ÇEKME ---
                # "2025-2026 I. DÖNEM PUAN ÇİZELGESİ" metninden ilgili kısmı alır.
                donem_match = re.search(r"(\d{4}-\d{4}\s+[Iİ12]+\.\s*DÖNEM)", text, re.IGNORECASE)
                ders_adi_match = re.search(r"(?:Dersin Adı|Ders Adı|Dersi)\s*:\s*(.*)", text, re.IGNORECASE)
                sinif_match = re.search(r"(?:Sınıfı / Şubesi|Sınıfı|Sınıf)\s*:\s*(.*)", text, re.IGNORECASE)
                
                donem_bilgisi = donem_match.group(1).strip().upper() if donem_match else "Bilinmeyen Dönem"
                ders_adi = ders_adi_match.group(1).strip() if ders_adi_match else "Bilinmiyor"
                sinif_bilgisi = sinif_match.group(1).strip() if sinif_match else "Bilinmiyor"
                
                unique_key = (sinif_bilgisi, ders_adi, donem_bilgisi)
                if unique_key in islenen_dersler_listesi:
                    print(f"ATLANDI: Sayfa {i+1} -> {sinif_bilgisi} | {ders_adi} ({donem_bilgisi} - Zaten alındı)")
                    continue
                
                tablo = sayfa.extract_table(table_settings=tablo_ayarlari)
                if not tablo: continue

                islenen_dersler_listesi.add(unique_key)
                satir_sayaci = 0

                for satir in tablo:
                    if not satir or len(satir) < 5: continue
                    
                    # --- DİNAMİK SÜTUN BULUCU ---
                    sira_no_index = -1
                    if satir[0] and str(satir[0]).isdigit():
                        sira_no_index = 0  # Mock PDF (Chrome çıktısı)
                    elif len(satir) > 1 and satir[1] and str(satir[1]).isdigit():
                        sira_no_index = 1  # Gerçek E-Okul PDF'i
                    
                    if sira_no_index == -1:
                        continue
                    
                    def not_temizle(deger):
                        if deger == "G" or deger == "g": return 0.0
                        if deger == "" or deger is None: return None
                        try: return float(str(deger).replace(",", "."))
                        except ValueError: return None

                    try:
                        # --- DÖNEM BİLGİSİ SÖZLÜĞE EKLENDİ ---
                        ogrenci_verisi = {
                            "dosya": os.path.basename(dosya_yolu),
                            "donem": donem_bilgisi, # Veritabanı için kritik alan!
                            "sinif": sinif_bilgisi,
                            "ders": ders_adi,
                            "ogrenci_no": satir[sira_no_index + 1], 
                            "ad_soyad": satir[sira_no_index + 2].replace("\n", " "),
                            "y1": not_temizle(satir[sira_no_index + 3]), 
                            "y2": not_temizle(satir[sira_no_index + 4]),
                            "y3": not_temizle(satir[sira_no_index + 5]),
                            "y4": not_temizle(satir[sira_no_index + 6]),
                            "y5": not_temizle(satir[sira_no_index + 7]),
                            "os": not_temizle(satir[sira_no_index + 8]),
                            "p1": not_temizle(satir[sira_no_index + 9]),
                            "p2": not_temizle(satir[sira_no_index + 10]),
                            "p3": not_temizle(satir[sira_no_index + 11]),
                            "u1": not_temizle(satir[sira_no_index + 12]),
                            "u2": not_temizle(satir[sira_no_index + 13]),
                            "u3": not_temizle(satir[sira_no_index + 14]),
                            "proje": not_temizle(satir[sira_no_index + 15]),
                            "muaf": satir[sira_no_index + 16],
                            "ortalama": not_temizle(satir[sira_no_index + 17])
                        }
                        tum_veriler.append(ogrenci_verisi)
                        satir_sayaci += 1
                    except IndexError:
                        continue
                
                print(f"OKUNDU: Sayfa {i+1} -> {sinif_bilgisi} | {ders_adi} ({satir_sayaci} Öğr.)")

    return tum_veriler

def sinif_ekle_ve_id_al(sinif_adi):
    conn = sqlite3.connect('okul_verisi.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO siniflar (sinif_adi) VALUES (?)", (sinif_adi,))
    cursor.execute("SELECT id FROM siniflar WHERE sinif_adi = ?", (sinif_adi,))
    sonuc = cursor.fetchone()
    conn.commit()
    conn.close()
    return sonuc[0] if sonuc else None

def ogrenci_ekle(okul_no, ad_soyad, sinif_id):
    conn = sqlite3.connect('okul_verisi.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO ogrenciler (okul_no, ad_soyad, sinif_id) VALUES (?, ?, ?)", (okul_no, ad_soyad, sinif_id))
    conn.commit()
    conn.close()

def not_ekle(okul_no, ders_adi, donem, y1, y2, y3, y4, y5, os, p1, p2, p3, u1, u2, u3, proje, muaf, ortalama):
    conn = sqlite3.connect('okul_verisi.db')
    cursor = conn.cursor()
    # INSERT OR REPLACE: Öğrencinin o dönemdeki notu zaten varsa YENİSİYLE GÜNCELLE!
    cursor.execute('''INSERT OR REPLACE INTO notlar 
        (okul_no, ders_adi, donem, y1, y2, y3, y4, y5, os, p1, p2, p3, u1, u2, u3, proje, muaf, ortalama) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
        (okul_no, ders_adi, donem, y1, y2, y3, y4, y5, os, p1, p2, p3, u1, u2, u3, proje, muaf, ortalama))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("PDF verileri okunuyor...")
    
    # Klasör yolunu kendi bilgisayarına göre ayarla
    cekilen_veriler = eokul_pdf_parser_smart("./veri_pdf") 
    
    for ogr in cekilen_veriler:
        
        donem_bilgisi = ogr.get("donem", "2025-2026 I. Dönem")

        # 1. Sınıfı ekle / ID'sini al
        sinif_id = sinif_ekle_ve_id_al(ogr["sinif"])
        
        # 2. Öğrenciyi ekle (Öğrenci zaten varsa hata vermez, geçer)
        ogrenci_ekle(ogr["ogrenci_no"], ogr["ad_soyad"], sinif_id)
        
        # 3. Notları ekle veya GÜNCELLE (INSERT OR REPLACE)
        not_ekle(
            ogr["ogrenci_no"], ogr["ders"], donem_bilgisi,
            ogr["y1"], ogr["y2"], ogr["y3"], ogr["y4"], ogr["y5"],
            ogr["os"], ogr["p1"], ogr["p2"], ogr["p3"], 
            ogr["u1"], ogr["u2"], ogr["u3"], 
            ogr["proje"], ogr["muaf"], ogr["ortalama"]
        )
        
    print(f"BAŞARILI! Toplam {len(cekilen_veriler)} kayıt veritabanına işlendi/güncellendi!")