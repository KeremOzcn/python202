# Kütüphane Yönetim Sistemi

Global AI Hub Python 202 Bootcamp Projesi - Üç aşamalı kütüphane yönetim uygulaması

## Proje Açıklaması

Bu proje, Python'da Nesne Yönelimli Programlama (OOP), Harici API Kullanımı ve FastAPI ile Web Servisi geliştirme konularını birleştiren kapsamlı bir öğrenme projesidir. Proje üç aşamadan oluşur:

1. **Aşama 1**: OOP ile konsol tabanlı kütüphane uygulaması
2. **Aşama 2**: Open Library API entegrasyonu ile otomatik kitap bilgisi çekme
3. **Aşama 3**: FastAPI ile REST API web servisi

## Özellikler

### 🏛️ Temel Kütüphane İşlemleri
- Kitap ekleme (manuel ve API ile otomatik)
- Kitap silme
- Kitap listeleme
- Kitap arama (başlık, yazar, ISBN)
- JSON dosyasında kalıcı veri saklama

### 🌐 API Entegrasyonu
- Open Library API ile otomatik kitap bilgisi çekme
- Hata yönetimi ve timeout kontrolü
- İnternet bağlantısı sorunlarına karşı dayanıklılık

### 🚀 Web API Servisi
- RESTful API endpoint'leri
- Otomatik API dokümantasyonu (Swagger/OpenAPI)
- Pydantic ile veri doğrulama
- JSON yanıtları

## Kurulum

### Gereksinimler
- Python 3.8+
- pip (Python paket yöneticisi)

### Adımlar

1. **Repoyu klonlayın:**
```bash
git clone <repo-url>
cd python202
```

2. **Sanal ortam oluşturun (önerilen):**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Bağımlılıkları kurun:**
```bash
pip install -r requirements.txt
```

## Kullanım

### 🖥️ Konsol Uygulaması (Aşama 1 & 2)

```bash
python main.py
```

**Menü Seçenekleri:**
- `1` - Kitap Ekle (API ile otomatik veya manuel)
- `2` - Kitap Sil
- `3` - Kitapları Listele
- `4` - Kitap Ara
- `5` - Kütüphane İstatistikleri
- `6` - Çıkış

### 🌐 Web API Servisi (Aşama 3)

```bash
uvicorn api:app --reload
```

API sunucusu `http://localhost:8000` adresinde çalışacaktır.

**Interaktif API Dokümantasyonu:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoint'leri

### 📚 Kitap İşlemleri

| Method | Endpoint | Açıklama | Body Örneği |
|--------|----------|----------|-------------|
| `GET` | `/books` | Tüm kitapları listele | - |
| `POST` | `/books` | ISBN ile kitap ekle | `{"isbn": "978-0451524935"}` |
| `POST` | `/books/manual` | Manuel kitap ekle | `{"title": "1984", "author": "George Orwell", "isbn": "978-0451524935"}` |
| `GET` | `/books/{isbn}` | Belirli kitabı getir | - |
| `DELETE` | `/books/{isbn}` | Kitap sil | - |
| `GET` | `/books/search/{query}` | Kitap ara | - |
| `GET` | `/stats` | Kütüphane istatistikleri | - |

### 📖 API Kullanım Örnekleri

**Kitap ekleme (ISBN ile):**
```bash
curl -X POST "http://localhost:8000/books" \
     -H "Content-Type: application/json" \
     -d '{"isbn": "978-0451524935"}'
```

**Manuel kitap ekleme:**
```bash
curl -X POST "http://localhost:8000/books/manual" \
     -H "Content-Type: application/json" \
     -d '{"title": "1984", "author": "George Orwell", "isbn": "978-0451524935"}'
```

**Kitap arama:**
```bash
curl "http://localhost:8000/books/search/Orwell"
```

## Test Etme

### 🧪 Otomatik Testler

```bash
# Tüm testleri çalıştır
python -m pytest test_library.py -v

# Veya test dosyasını doğrudan çalıştır
python test_library.py
```

### 📊 Test Kapsamı
- Book sınıfı testleri
- Library sınıfı testleri
- API entegrasyonu testleri (mock'lanmış)
- Dosya işlemleri testleri
- Hata durumu testleri

## Proje Yapısı

```
library-management/
├── main.py              # Ana konsol uygulaması
├── book.py              # Book sınıfı
├── library.py           # Library sınıfı + API entegrasyonu
├── api.py               # FastAPI web servisi
├── test_library.py      # Pytest testleri
├── requirements.txt     # Python bağımlılıkları
├── README.md           # Bu dosya
├── library.json        # Konsol uygulaması veri dosyası
└── api_library.json    # Web API veri dosyası
```

## Teknolojiler

- **Python 3.8+**: Ana programlama dili
- **httpx**: HTTP istemcisi (Open Library API)
- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI sunucusu
- **Pydantic**: Veri doğrulama
- **pytest**: Test framework
- **JSON**: Veri depolama formatı

## API Entegrasyonu

Proje, [Open Library API](https://openlibrary.org/developers/api) kullanarak kitap bilgilerini otomatik olarak çeker:

- **Endpoint**: `https://openlibrary.org/isbn/{isbn}.json`
- **Yazar Bilgileri**: `https://openlibrary.org/authors/{author_key}.json`
- **Hata Yönetimi**: 404, timeout ve bağlantı hataları
- **Fallback**: Manuel kitap ekleme seçeneği

## Geliştirme Notları

### 🔧 Gelecek Geliştirmeler
- SQLite veritabanı entegrasyonu
- PUT endpoint'i ile kitap güncelleme
- HTML/CSS/JavaScript frontend
- Docker containerization
- Kullanıcı kimlik doğrulama
- Kitap kategorileri ve etiketleme

### 🐛 Bilinen Sınırlamalar
- Open Library API bazen yavaş yanıt verebilir
- Bazı kitaplar için yazar bilgisi eksik olabilir
- Sadece ISBN-10 ve ISBN-13 formatları desteklenir

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın
