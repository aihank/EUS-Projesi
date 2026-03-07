🕵️‍♂️ Bölüm 3: Python ile Kusursuz PDF Madenciliği

YouTube serimizin 3. videosunda yapay zekaya bir PDF okuma kodu yazdırmıştık. Ancak videonun sonunda da belirttiğim gibi; gerçek ve karmaşık E-Okul PDF'lerinde yapay zekanın yazdığı o temel kod maalesef yetersiz kalıyor! (Sütun kaymaları oluyor ve "G" - Girmedi gibi değerlerde kod çöküyor).

Bu yüzden repoya, videodaki hatalı kodu değil; "Kusursuz PDF Okuyucu" kodunu yükledim.

🌟 Bu Koddaki Yenilikler (Videodan Farkı)

Dinamik Sütun Bulucu (sira_no_index): E-Okul tablolarındaki gizli çizgiler yüzünden yaşanan sütun kaymalarını otomatik tespit eder ve notları asla yanlış hücreye yazmaz.

Tüm Notları Sömürme: Sadece Y1 ve Y2'yi değil; Y3, Y4, OS, Proje, Uygulama ve P1, P2 dahil tablodaki tüm potansiyel notları eksiksiz çeker. (Video 4'teki Veritabanı mimarimiz için bu şarttı!)

Temizleme Filtresi: Boş hücreleri None, "G" (Girmedi) harflerini ise 0.0 olarak matematiksel işleme hazır hale getirir.

🚀 Nasıl Çalıştırılır?

Bilgisayarınızda kütüphanelerin yüklü olduğundan emin olun:
pip install pdfplumber pandas

Kodu çalıştıracağınız dizinde veri_pdf adında bir klasör oluşturun (veya bu repodaki hazır klasörü kullanın).

Test PDF'lerinizi o klasörün içine atın ve Python dosyasını çalıştırın!

python eokul_kusursuz_okuyucu.py
