#!/usr/bin/env python3
"""
Kütüphane Yönetim Sistemi - Pytest Testleri
Global AI Hub Python 202 Bootcamp Projesi - Aşama 1
"""

import pytest
import os
import json
import tempfile
import httpx
from unittest.mock import patch, Mock
from book import Book
from library import Library


class TestBook:
    """Book sınıfı için test sınıfı."""
    
    def test_book_creation(self):
        """Book nesnesinin doğru oluşturulduğunu test eder."""
        book = Book("1984", "George Orwell", "978-0451524935")
        
        assert book.title == "1984"
        assert book.author == "George Orwell"
        assert book.isbn == "978-0451524935"
        
    def test_book_creation_with_html(self):
        """HTML içeren girişlerin düzgün şekilde escape edildiğini test eder."""
        book = Book("<script>alert('xss')</script>", "<b>Hacker</b>", "123-4567890123")
        
        assert "<script>" not in book.title
        assert "<b>" not in book.author
        assert book.isbn == "123-4567890123"
        
    def test_book_creation_invalid_isbn(self):
        """Geçersiz ISBN ile kitap oluşturulduğunda hata verdiğini test eder."""
        with pytest.raises(ValueError):
            Book("Test", "Author", "invalid-isbn!")
            
    def test_book_creation_empty_fields(self):
        """Boş alanlarla kitap oluşturulduğunda hata verdiğini test eder."""
        with pytest.raises(ValueError):
            Book("", "Author", "1234567890")
        with pytest.raises(ValueError):
            Book("Title", "", "1234567890")
        with pytest.raises(ValueError):
            Book("Title", "Author", "")
    
    def test_book_str_representation(self):
        """Book nesnesinin string temsilini test eder."""
        book = Book("Ulysses", "James Joyce", "978-0199535675")
        expected = "Ulysses by James Joyce (ISBN: 978-0199535675)"
        
        assert str(book) == expected
    
    def test_book_repr_representation(self):
        """Book nesnesinin repr temsilini test eder."""
        book = Book("Test Book", "Test Author", "123456789")
        expected = "Book(title='Test Book', author='Test Author', isbn='123456789')"
        
        assert repr(book) == expected
    
    def test_book_to_dict(self):
        """Book nesnesinin dictionary'ye çevrilmesini test eder."""
        book = Book("Test Title", "Test Author", "123456789")
        expected_dict = {
            "title": "Test Title",
            "author": "Test Author",
            "isbn": "123456789"
        }
        
        assert book.to_dict() == expected_dict
    
    def test_book_from_dict(self):
        """Dictionary'den Book nesnesinin oluşturulmasını test eder."""
        book_dict = {
            "title": "Test Title",
            "author": "Test Author",
            "isbn": "123456789"
        }
        
        book = Book.from_dict(book_dict)
        
        assert book.title == "Test Title"
        assert book.author == "Test Author"
        assert book.isbn == "123456789"


class TestLibrary:
    """Library sınıfı için test sınıfı."""
    
    @pytest.fixture
    def temp_library(self):
        """Her test için geçici bir kütüphane oluşturur."""
        # Geçici dosya oluştur
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()
        
        library = Library(temp_file.name)
        
        yield library
        
        # Test sonrası temizlik
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    @pytest.fixture
    def sample_books(self):
        """Test için örnek kitaplar."""
        return [
            Book("1984", "George Orwell", "978-0451524935"),
            Book("To Kill a Mockingbird", "Harper Lee", "978-0061120084"),
            Book("The Great Gatsby", "F. Scott Fitzgerald", "978-0743273565")
        ]
    
    def test_library_creation(self, temp_library):
        """Library nesnesinin doğru oluşturulduğunu test eder."""
        assert isinstance(temp_library.books, list)
        assert len(temp_library.books) == 0
        assert temp_library.get_book_count() == 0
    
    def test_add_book_success(self, temp_library, sample_books):
        """Kitap ekleme işleminin başarılı olduğunu test eder."""
        book = sample_books[0]
        result = temp_library.add_book(book)
        
        assert result is True
        assert temp_library.get_book_count() == 1
        assert temp_library.find_book(book.isbn) == book
    
    def test_add_book_duplicate_isbn(self, temp_library, sample_books):
        """Aynı ISBN'li kitap eklemeye çalışıldığında hata verdiğini test eder."""
        book1 = sample_books[0]
        book2 = Book("Different Title", "Different Author", book1.isbn)
        
        temp_library.add_book(book1)
        result = temp_library.add_book(book2)
        
        assert result is False
        assert temp_library.get_book_count() == 1
    
    def test_remove_book_success(self, temp_library, sample_books):
        """Kitap silme işleminin başarılı olduğunu test eder."""
        book = sample_books[0]
        temp_library.add_book(book)
        
        result = temp_library.remove_book(book.isbn)
        
        assert result is True
        assert temp_library.get_book_count() == 0
        assert temp_library.find_book(book.isbn) is None
    
    def test_remove_book_not_found(self, temp_library):
        """Olmayan kitap silmeye çalışıldığında hata verdiğini test eder."""
        result = temp_library.remove_book("nonexistent-isbn")
        
        assert result is False
        assert temp_library.get_book_count() == 0
    
    def test_find_book_success(self, temp_library, sample_books):
        """Kitap bulma işleminin başarılı olduğunu test eder."""
        book = sample_books[0]
        temp_library.add_book(book)
        
        found_book = temp_library.find_book(book.isbn)
        
        assert found_book == book
        assert found_book.title == book.title
        assert found_book.author == book.author
    
    def test_find_book_not_found(self, temp_library):
        """Olmayan kitap arandığında None döndürdüğünü test eder."""
        result = temp_library.find_book("nonexistent-isbn")
        
        assert result is None
    
    def test_search_books_by_title(self, temp_library, sample_books):
        """Başlığa göre kitap arama işlemini test eder."""
        for book in sample_books:
            temp_library.add_book(book)
        
        # "Great" kelimesini ara
        results = temp_library.search_books("Great")
        
        assert len(results) == 1
        assert results[0].title == "The Great Gatsby"
    
    def test_search_books_by_author(self, temp_library, sample_books):
        """Yazara göre kitap arama işlemini test eder."""
        for book in sample_books:
            temp_library.add_book(book)
        
        # "Orwell" kelimesini ara
        results = temp_library.search_books("Orwell")
        
        assert len(results) == 1
        assert results[0].author == "George Orwell"
    
    def test_search_books_case_insensitive(self, temp_library, sample_books):
        """Arama işleminin büyük/küçük harf duyarsız olduğunu test eder."""
        book = sample_books[0]
        temp_library.add_book(book)
        
        # Küçük harfle ara
        results = temp_library.search_books("george")
        
        assert len(results) == 1
        assert results[0].author == "George Orwell"
    
    def test_search_books_no_results(self, temp_library, sample_books):
        """Arama sonucu bulunamadığında boş liste döndürdüğünü test eder."""
        for book in sample_books:
            temp_library.add_book(book)
        
        results = temp_library.search_books("nonexistent")
        
        assert len(results) == 0
        assert results == []
    
    def test_get_all_books(self, temp_library, sample_books):
        """Tüm kitapları alma işlemini test eder."""
        for book in sample_books:
            temp_library.add_book(book)
        
        all_books = temp_library.get_all_books()
        
        assert len(all_books) == len(sample_books)
        assert all_books is not temp_library.books  # Kopya olduğunu kontrol et (farklı nesne)
    
    def test_save_and_load_books(self, temp_library, sample_books):
        """Kitapları kaydetme ve yükleme işlemini test eder."""
        # Kitapları ekle
        for book in sample_books:
            temp_library.add_book(book)
        
        # Yeni kütüphane oluştur (aynı dosyadan yükleyecek)
        new_library = Library(temp_library.filename)
        
        assert new_library.get_book_count() == len(sample_books)
        
        # Her kitabın doğru yüklendiğini kontrol et
        for original_book in sample_books:
            loaded_book = new_library.find_book(original_book.isbn)
            assert loaded_book is not None
            assert loaded_book.title == original_book.title
            assert loaded_book.author == original_book.author
            assert loaded_book.isbn == original_book.isbn
    
    def test_load_books_file_not_exists(self):
        """Dosya yokken kütüphane oluşturulduğunu test eder."""
        nonexistent_file = "nonexistent_library.json"
        
        # Dosyanın olmadığından emin ol
        if os.path.exists(nonexistent_file):
            os.unlink(nonexistent_file)
        
        library = Library(nonexistent_file)
        
        assert library.get_book_count() == 0
        assert isinstance(library.books, list)
        
        # Temizlik
        if os.path.exists(nonexistent_file):
            os.unlink(nonexistent_file)
    
    def test_load_books_invalid_json(self):
        """Bozuk JSON dosyası olduğunda yeni kütüphane oluşturulduğunu test eder."""
        # Geçici bozuk JSON dosyası oluştur
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write("invalid json content")
        temp_file.close()
        
        library = Library(temp_file.name)
        
        assert library.get_book_count() == 0
        assert isinstance(library.books, list)
        
        # Temizlik
        os.unlink(temp_file.name)


class TestLibraryAPI:
    """Library sınıfının API fonksiyonları için test sınıfı."""
    
    @pytest.fixture
    def temp_library(self):
        """Her test için geçici bir kütüphane oluşturur."""
        # Geçici dosya oluştur
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()
        
        library = Library(temp_file.name)
        
        yield library
        
        # Test sonrası temizlik
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    @pytest.fixture
    def mock_client(self):
        """HTTP istekleri için mock client oluşturur."""
        with patch('httpx.Client') as mock:
            yield mock
            
    @pytest.fixture
    def sample_book_data(self):
        """Örnek kitap verisi döndürür."""
        return {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "1234567890"
        }
    
    def test_add_book_by_isbn_invalid_isbn(self, temp_library):
        """Geçersiz ISBN ile kitap eklemeye çalışıldığında hata döndürdüğünü test eder."""
        # Geçersiz ISBN formatları
        invalid_isbns = [
            "",  # Boş string
            "   ",  # Sadece boşluk
            "abc123",  # Geçersiz karakterler
            "123456789012345678901"  # Çok uzun
        ]
        
        for isbn in invalid_isbns:
            with pytest.raises(ValueError) as exc_info:
                temp_library.add_book_by_isbn(isbn)
            # Check for either "geçersiz" or "bulunamadı" since invalid ISBNs may trigger API calls
            error_msg = str(exc_info.value).lower()
            assert "geçersiz" in error_msg or "bulunamadı" in error_msg
            
        # Kitap eklenmediğini kontrol et
        assert len(temp_library.books) == 0
            
    @patch('library.httpx.Client')
    def test_fetch_book_from_api_success(self, mock_client, temp_library):
        """API'den kitap bilgilerini başarıyla çekmeyi test eder."""
        # Mock yanıtı oluştur
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "<script>Test Book</script>",  # Test XSS koruması
            "authors": [{"key": "/authors/OL1A"}]
        }
        
        # Yazar bilgisi için mock yanıtı
        mock_author_response = Mock()
        mock_author_response.status_code = 200
        mock_author_response.json.return_value = {
            "name": "<b>Test Author</b>"  # Test XSS koruması
        }
        
        # Mock client'ı ayarla
        mock_client.return_value.__enter__.return_value.get.side_effect = [
            mock_response,
            mock_author_response
        ]
        
        # Test et
        result = temp_library.fetch_book_from_api("1234567890")
        
        assert result is not None
        # API layer doesn't escape HTML - Book class will handle it
        assert result["title"] == "<script>Test Book</script>"
        assert result["author"] == "<b>Test Author</b>"
        
        # ISBN'in doğru şekilde ayarlandığını kontrol et
        assert result["isbn"] == "1234567890"
        
        # API çağrılarının doğru yapıldığını doğrula
        mock_client.return_value.__enter__.return_value.get.assert_any_call(
            "https://openlibrary.org/isbn/1234567890.json"
        )
        mock_client.return_value.__enter__.return_value.get.assert_any_call(
            "https://openlibrary.org/authors/OL1A.json"
        )
    
    @patch('library.httpx.Client')
    def test_fetch_book_from_api_not_found(self, mock_client, temp_library):
        """API'de kitap bulunamadığında hata döndürdüğünü test eder."""
        # Mock yanıtı oluştur (404 Not Found)
        mock_response = Mock()
        mock_response.status_code = 404
        
        # Mock client'ı ayarla
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        
        # Test et - hata fırlatmalı
        with pytest.raises(ValueError) as exc_info:
            temp_library.fetch_book_from_api("nonexistent123")
            
        # Hata mesajının doğru olduğunu kontrol et
        assert "bulunamadı" in str(exc_info.value).lower()
        
        # API çağrısının doğru yapıldığını doğrula
        mock_client.return_value.__enter__.return_value.get.assert_called_once_with(
            "https://openlibrary.org/isbn/nonexistent123.json"
        )
    
    @patch('library.httpx.Client')
    def test_fetch_book_from_api_timeout(self, mock_client, temp_library):
        """API timeout durumunda uygun hata döndürdüğünü test eder."""
        # Timeout hatası oluştur
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.TimeoutException("Timeout")
        
        # Test et - hata fırlatmalı
        with pytest.raises(ValueError) as exc_info:
            temp_library.fetch_book_from_api("timeout123")
            
        # Hata mesajının doğru olduğunu kontrol et
        assert "ağ hatası" in str(exc_info.value).lower()
        
        # API çağrısının doğru yapıldığını doğrula
        mock_client.return_value.__enter__.return_value.get.assert_called_once()
    
    @patch('library.httpx.Client')
    def test_add_book_by_isbn_success(self, mock_client, temp_library):
        """ISBN ile kitap eklemenin başarılı olduğunu test eder."""
        # Mock yanıtları oluştur
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "<script>Test Book</script>",  # Test XSS koruması
            "authors": [{"key": "/authors/OL1A"}]
        }
        
        mock_author_response = Mock()
        mock_author_response.status_code = 200
        mock_author_response.json.return_value = {
            "name": "<b>Test Author</b>"  # Test XSS koruması
        }
        
        # Mock client'ı ayarla
        mock_client.return_value.__enter__.return_value.get.side_effect = [
            mock_response,
            mock_author_response
        ]
        
        # Test et
        result = temp_library.add_book_by_isbn("123-4567890")
        
        assert result is True
        assert len(temp_library.books) == 1
        book = temp_library.books[0]
        assert book.isbn == "123-4567890"
        assert book.title == "&lt;script&gt;Test Book&lt;/script&gt;"  # HTML escape edilmiş olmalı
        assert book.author == "&lt;b&gt;Test Author&lt;/b&gt;"  # HTML escape edilmiş olmalı
        
        # Aynı ISBN ile tekrar eklemeye çalış - hata vermeli
        with pytest.raises(ValueError) as exc_info:
            temp_library.add_book_by_isbn("123-4567890")
        assert "zaten mevcut" in str(exc_info.value)
        
        # API çağrılarının doğru yapıldığını doğrula
        assert mock_client.return_value.__enter__.return_value.get.call_count == 2
    
    def test_add_book_by_isbn_duplicate(self, temp_library, sample_book_data):
        """Aynı ISBN'li kitap eklemeye çalışıldığında hata döndürdüğünü test eder."""
        # Önce bir kitap ekle
        book = Book(**sample_book_data)
        temp_library.add_book(book)
        
        # Aynı ISBN ile tekrar eklemeye çalış - hata fırlatmalı
        with pytest.raises(ValueError) as exc_info:
            temp_library.add_book_by_isbn(sample_book_data["isbn"])
            
        # Hata mesajının doğru olduğunu kontrol et
        assert "zaten mevcut" in str(exc_info.value).lower()
        
        # Kitap sayısının değişmediğini kontrol et
        assert len(temp_library.books) == 1
    
    @patch('library.httpx.Client')
    def test_add_book_by_isbn_api_failure(self, mock_client, temp_library):
        """API başarısız olduğunda uygun hata döndürdüğünü test eder."""
        # Hata durumu için mock yanıtı (500 Internal Server Error)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        
        # Test et - hata fırlatmalı
        with pytest.raises(ValueError) as exc_info:
            temp_library.add_book_by_isbn("error123")
            
        # Hata mesajının doğru olduğunu kontrol et
        assert "başarısız oldu" in str(exc_info.value).lower()
        
        # Kitap eklenmediğini kontrol et
        assert len(temp_library.books) == 0
        
        # API çağrısının doğru yapıldığını doğrula
        mock_client.return_value.__enter__.return_value.get.assert_called_once_with(
            "https://openlibrary.org/isbn/error123.json"
        )


# Test çalıştırma fonksiyonu
def run_tests():
    """Testleri çalıştırır ve sonuçları yazdırır."""
    print("Kütüphane Yönetim Sistemi - Test Sonuçları")
    print("=" * 50)
    
    # pytest'i programatik olarak çalıştır
    pytest_args = [__file__, "-v", "--tb=short"]
    result = pytest.main(pytest_args)
    
    if result == 0:
        print("\n✅ Tüm testler başarıyla geçti!")
    else:
        print(f"\n❌ Bazı testler başarısız oldu. Çıkış kodu: {result}")
    
    return result


if __name__ == "__main__":
    run_tests()
