from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'eus_cok_gizli_anahtar_123' 

# --- KURŞUN GEÇİRMEZ VERİTABANI YOLU ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'okul_verisi.db')

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

# --- ROUTE: ÇIKIŞ YAP ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db_defaults() 
    app.run(debug=True)