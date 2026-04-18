🚀 Okul Erken Uyarı Sistemi (EUS) - Python Projesi



Bu depo, YouTube kanalımızda adım adım geliştirdiğimiz "Okul Erken Uyarı Sistemi (EUS)" projesinin kaynak kodlarını içerir. Projenin amacı, okullardaki dağınık verileri (Notlar, Devamsızlıklar) Python ile analiz ederek risk altındaki öğrencileri yapay zeka ve veri madenciliği ile önceden tespit etmektir.



📺 YouTube Eğitim Serisi ve Kodlar



Proje kodları, videolardaki ilerleyişe göre klasörlere ayrılmıştır. Yeni videolar yayınlandıkça bu depo güncellenecektir.



📁 Bölüm 2: Yapay Zeka ile Test Verisi Üretimi (YAYINDA!)



Gerçek öğrenci verilerini tehlikeye atmamak (KVKK uyumu) için yapay zeka yardımıyla hazırladığımız, E-Okul formatında birebir "Test PDF Üreticisi" HTML şablonu.



📁 Bölüm 3: Python ile PDF Madenciliği (YAYINDA!)



pdfplumber kullanarak PDF'lerdeki notları, sütun kaymalarına bağışıklı bir şekilde (Regex ile) çeken kusursuz Python kodları.


📁 Bölüm 4: Sistemin Beyni - SQLite Veritabanı (YAYINDA!)

Çekilen verilerin okul_verisi.db içine ilişkisel tablolarla, "INSERT OR REPLACE" (Snapshot) mantığı kullanılarak yazılması.


📁 Bölüm 5: Devamsızlık Analizi ve Excel Okuma (YAYINDA!)

Devamsızlık için .xls dosyalarını Pandas ile okuma, Regex ile çöp verileri temizleme ve devamsızlıkları "Trend Analizi" (Time-Series) mantığıyla veritabanına kaydetme. (Not: Videoda bahsedilen mazeretli/mazeretsiz ters yazım hatası buradaki kodlarda giderilmiştir.)

📁 Bölüm 6: Web Arayüzü ve Yetkilendirme (YAYINDA!)

Siyah terminal ekranından çıkış! Flask ile Dashboard kurulumu, werkzeug.security ile şifreli giriş (Login), Session yönetimi ve Role Dayalı Erişim Kontrolü (RBAC) ile güvenli web altyapısı.

📁 Bölüm 7: Admin Paneli ve Dosya Yükleme (YAYINDA!)

Siyah ekrana kod yazmaya son! Web arayüzü üzerinden PDF (Notlar) ve Excel (Devamsızlık) dosyalarını seçip doğrudan sisteme yükleme ve Python veri okuyucu scriptlerinin web'e entegrasyonu.

🔒 Bölüm 8: Büyük Final - Risk Algoritması (Yakında)

Toplanan not ve devamsızlık verilerinin formülize edilip "Erken Uyarı Risk Puanı" hesaplanması ve Dashboard üzerinde kırmızı/sarı/yeşil alarmların yakılması.

⚙️ Nasıl Çalıştırılır?


Bölüm 2 İçin: Bolum\_2\_Test\_Verisi\_Uretimi klasöründeki .html dosyasını tarayıcınızda (Chrome/Edge) açın ve CTRL + P (Yazdır) diyerek "PDF Olarak Kaydet" seçeneğiyle kendi test verilerinizi üretin. 3. Bölümdeki Python kodları için bu PDF'leri kullanacağız!


Projeyi bilgisayarınızda çalıştırmak için gerekli kütüphaneleri kurmanız gerekmektedir. Terminalinize aşağıdaki komutu yazın:

pip install pdfplumber pandas openpyxl lxml Flask werkzeug

Daha sonra web sunucusunu başlatmak için proje dizininde:

python app.py

yazarak tarayıcınızdan http://127.0.0.1:5000 adresine gidebilirsiniz.

💡 Not: Bu proje eğitim amaçlıdır. Lütfen gerçek öğrenci verileriyle çalışırken KVKK (Kişisel Verilerin Korunması Kanunu) kurallarına azami özen gösteriniz.


