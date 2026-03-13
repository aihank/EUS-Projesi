import sqlite3

def veritabani_kur():
    conn = sqlite3.connect('okul_verisi.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS roller (id INTEGER PRIMARY KEY AUTOINCREMENT, rol_adi TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS kullanicilar (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT, sifre_hash TEXT, rol_id INTEGER, FOREIGN KEY (rol_id) REFERENCES roller(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS siniflar (id INTEGER PRIMARY KEY AUTOINCREMENT, sinif_adi TEXT UNIQUE, rehber_ogretmen_id INTEGER, FOREIGN KEY (rehber_ogretmen_id) REFERENCES kullanicilar(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ogrenciler (okul_no TEXT PRIMARY KEY, ad_soyad TEXT, sinif_id INTEGER, FOREIGN KEY (sinif_id) REFERENCES siniflar(id))''')
    
    # NOTLAR TABLOSU: Aynı dersten aynı dönemde 2. bir satır açmamak için UNIQUE (Snapshot mantığı)
    cursor.execute('''CREATE TABLE IF NOT EXISTS notlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT, okul_no TEXT, ders_adi TEXT, donem TEXT,
        y1 REAL, y2 REAL, y3 REAL, y4 REAL, y5 REAL, os REAL,
        p1 REAL, p2 REAL, p3 REAL, u1 REAL, u2 REAL, u3 REAL,
        proje REAL, muaf TEXT, ortalama REAL,
        tarih DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (okul_no) REFERENCES ogrenciler(okul_no),
        UNIQUE(okul_no, ders_adi, donem)
    )''')
    
    # DEVAMSIZLIK TABLOSU: Zaman içindeki değişimi (trend) görmek için UNIQUE YOK! Alt alta ekler.
    cursor.execute('''CREATE TABLE IF NOT EXISTS devamsizlik (
        id INTEGER PRIMARY KEY AUTOINCREMENT, okul_no TEXT, donem TEXT, 
        mazeretli REAL, mazeretsiz REAL, toplam REAL, 
        tarih DATETIME DEFAULT CURRENT_TIMESTAMP, 
        FOREIGN KEY (okul_no) REFERENCES ogrenciler(okul_no)
    )''')
    
    conn.commit()
    conn.close()
    print("Sistemin Beyni (okul_verisi.db) başarıyla inşa edildi! Tablolar hazır.")

if __name__ == "__main__":
    veritabani_kur()