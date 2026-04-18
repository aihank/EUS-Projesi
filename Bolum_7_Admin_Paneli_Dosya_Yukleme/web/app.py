from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os

from pdf_okuyucu_final_donem import eokul_pdf_parser_smart
from devamsizlik_2 import rapor_isleme

app = Flask(__name__)
app.secret_key = 'eus_cok_gizli_anahtar_123' 

# --- KURŞUN GEÇİRMEZ VERİTABANI YOLU ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'okul_verisi.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'yuklemeler')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --- İLK KURULUM: VARSAYILAN KULLANICILAR VE ROLLER ---
def init_db_defaults():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    roller = ['Admin', 'Rehberlik', 'Sınıf Öğretmeni']
    kullanicilar = [
        ('admin', '1234', 'Admin'),
        ('rehberlik', '1234', 'Rehberlik'),
        ('ogretmen', '1234', 'Sınıf Öğretmeni')
    ]
    
    # 1. Rolleri Ekle
    for rol in roller:
        cursor.execute("INSERT OR IGNORE INTO roller (rol_adi) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM roller WHERE rol_adi = ?)", (rol, rol))
        
    # 2. Kullanıcıları Ekle
    hashed_pw = generate_password_hash('1234')
    for k_adi, sifre, rol_adi in kullanicilar:
        cursor.execute("SELECT id FROM roller WHERE rol_adi = ?", (rol_adi,))
        rol_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = ?", (k_adi,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre_hash, rol_id) VALUES (?, ?, ?)", 
                           (k_adi, hashed_pw, rol_id))
            print(f"Sisteme eklendi: {k_adi} ({rol_adi})")
            
    conn.commit()
    conn.close()

# --- VERİ ÇEKME FONKSİYONU ---
def ogrenci_verilerini_getir():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    sorgu = """
        SELECT o.okul_no, o.ad_soyad, IFNULL(s.sinif_adi, 'Sınıfsız') as sinif,
               IFNULL(n.ortalama, 0) as ortalama, IFNULL(d.toplam, 0) as devamsizlik
        FROM ogrenciler o
        LEFT JOIN siniflar s ON o.sinif_id = s.id
        LEFT JOIN notlar n ON o.okul_no = n.okul_no
        LEFT JOIN devamsizlik d ON o.okul_no = d.okul_no
        GROUP BY o.okul_no ORDER BY o.okul_no ASC
    """
    cursor.execute(sorgu)
    veriler = cursor.fetchall()
    conn.close()
    return veriler

def sinif_ekle_ve_id_al(sinif_adi):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO siniflar (sinif_adi) VALUES (?)", (sinif_adi,))
    cursor.execute("SELECT id FROM siniflar WHERE sinif_adi = ?", (sinif_adi,))
    sonuc = cursor.fetchone()
    conn.commit()
    conn.close()
    return sonuc[0] if sonuc else None

def ogrenci_ekle(okul_no, ad_soyad, sinif_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO ogrenciler (okul_no, ad_soyad, sinif_id) VALUES (?, ?, ?)", (okul_no, ad_soyad, sinif_id))
    conn.commit()
    conn.close()

def not_ekle(okul_no, ders_adi, donem, y1, y2, y3, y4, y5, os, p1, p2, p3, u1, u2, u3, proje, muaf, ortalama):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # INSERT OR REPLACE: Öğrencinin o dönemdeki notu zaten varsa YENİSİYLE GÜNCELLE!
    cursor.execute('''INSERT OR REPLACE INTO notlar 
        (okul_no, ders_adi, donem, y1, y2, y3, y4, y5, os, p1, p2, p3, u1, u2, u3, proje, muaf, ortalama) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
        (okul_no, ders_adi, donem, y1, y2, y3, y4, y5, os, p1, p2, p3, u1, u2, u3, proje, muaf, ortalama))
    conn.commit()
    conn.close()

# --- ROUTE: GİRİŞ EKRANI ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        kadi = request.form['kullanici_adi']
        sifre = request.form['sifre']
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # JOIN ile kullanıcının rol adını da çekiyoruz!
        sorgu = """
            SELECT k.*, r.rol_adi 
            FROM kullanicilar k 
            JOIN roller r ON k.rol_id = r.id 
            WHERE k.kullanici_adi = ?
        """
        cursor.execute(sorgu, (kadi,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['sifre_hash'], sifre):
            session['user_id'] = user['id']
            session['username'] = user['kullanici_adi']
            session['rol'] = user['rol_adi'] # Rolü session'a attık
            return redirect(url_for('dashboard'))
        else:
            flash('Hatalı kullanıcı adı veya şifre!', 'error')
            
    return render_template('login.html')

# --- ROUTE: ANA SAYFA (DASHBOARD) ---
@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    ogrenciler = ogrenci_verilerini_getir()
    return render_template('index.html', ogrenciler=ogrenciler)


@app.route('/yukle', methods=['GET', 'POST'])
def dosya_yukle():
    if 'user_id' not in session or session.get('rol') != 'Admin':
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        islem_tipi = request.form.get('islem_tipi')
        dosya = request.files.get('dosya')
        
        if not dosya or dosya.filename == '':
            flash('Lütfen bir dosya seçin!', 'error')
            return redirect(request.url)
            
        filename = secure_filename(dosya.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        dosya.save(filepath)
        
        try:
            if islem_tipi == 'not_pdf' and filename.lower().endswith('.pdf'):
                veriler = eokul_pdf_parser_smart(app.config['UPLOAD_FOLDER'])
                
                if veriler:
                    for ogr in veriler:
                        donem_bilgisi = ogr.get("donem", "2025-2026 I. Dönem")
                        sinif_id = sinif_ekle_ve_id_al(ogr["sinif"])
                        ogrenci_ekle(ogr["ogrenci_no"], ogr["ad_soyad"], sinif_id)
                        not_ekle(
                            ogr["ogrenci_no"], ogr["ders"], donem_bilgisi,
                            ogr["y1"], ogr["y2"], ogr["y3"], ogr["y4"], ogr["y5"],
                            ogr["os"], ogr["p1"], ogr["p2"], ogr["p3"], 
                            ogr["u1"], ogr["u2"], ogr["u3"], 
                            ogr["proje"], ogr["muaf"], ogr["ortalama"]
                        )
                    flash(f'Harika! PDF işlendi. {len(veriler)} adet not kaydı veritabanına aktarıldı.', 'success')
                else:
                    flash('PDF okundu ancak geçerli tablo bulunamadı.', 'error')
                    
            elif islem_tipi == 'devam_excel' and filename.lower().endswith(('.xls', '.xlsx', '.csv', '.html')):
                rapor_isleme(filepath) 
                flash(f'Excel başarıyla analiz edildi ve devamsızlıklar veritabanına eklendi!', 'success')
                
            else:
                flash('Desteklenmeyen dosya formatı!', 'error')
                
        except Exception as e:
            flash(f'Sistem Hatası: {str(e)}', 'error')
            
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
                
        return redirect(url_for('dosya_yukle'))
        
    return render_template('yukle.html')

# --- ROUTE: ÇIKIŞ YAP ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db_defaults() 
    app.run(debug=True)