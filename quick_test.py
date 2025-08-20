#!/usr/bin/env python3
"""Hızlı test betiği - temel işlevselliği kontrol eder."""

def test_imports():
    """Import'ları test eder."""
    try:
        from book import Book
        from library import Library
        print("✓ Import'lar başarılı")
        return True
    except Exception as e:
        print(f"✗ Import hatası: {e}")
        return False

def test_book_creation():
    """Book sınıfını test eder."""
    try:
        from book import Book
        book = Book("Test Kitap", "Test Yazar", "123-4567890")
        print(f"✓ Book oluşturma başarılı: {book}")
        return True
    except Exception as e:
        print(f"✗ Book oluşturma hatası: {e}")
        return False

def test_library_creation():
    """Library sınıfını test eder."""
    try:
        from library import Library
        import tempfile
        import os
        
        # Geçici dosya oluştur
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_file.close()
        
        library = Library(temp_file.name)
        print("✓ Library oluşturma başarılı")
        
        # Temizlik
        os.unlink(temp_file.name)
        return True
    except Exception as e:
        print(f"✗ Library oluşturma hatası: {e}")
        return False

def test_add_book():
    """Kitap ekleme işlemini test eder."""
    try:
        from book import Book
        from library import Library
        import tempfile
        import os
        
        # Geçici dosya oluştur
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_file.close()
        
        library = Library(temp_file.name)
        book = Book("Test Kitap", "Test Yazar", "123-4567890")
        
        result = library.add_book(book)
        if result:
            print("✓ Kitap ekleme başarılı")
        else:
            print("✗ Kitap ekleme başarısız")
            
        # Temizlik
        os.unlink(temp_file.name)
        return result
    except Exception as e:
        print(f"✗ Kitap ekleme hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu."""
    print("=== Hızlı Test Başlıyor ===")
    
    tests = [
        ("Import'lar", test_imports),
        ("Book Oluşturma", test_book_creation),
        ("Library Oluşturma", test_library_creation),
        ("Kitap Ekleme", test_add_book)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} test ediliyor...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n=== Test Sonuçları ===")
    success_count = 0
    for test_name, success in results:
        status = "BAŞARILI" if success else "BAŞARISIZ"
        print(f"{test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\nToplam: {success_count}/{len(results)} test başarılı")
    
    if success_count == len(results):
        print("\n🎉 Tüm temel testler başarılı! Proje çalışır durumda.")
    else:
        print("\n⚠️ Bazı testler başarısız. Lütfen hataları kontrol edin.")

if __name__ == "__main__":
    main()
