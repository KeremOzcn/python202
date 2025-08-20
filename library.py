import json
import os
import html
import httpx
from typing import List, Optional
from book import Book


class Library:
    """
    Kütüphane yönetim sınıfı.
    
    Kitapları yönetir, JSON dosyasına kaydeder ve yükler.
    """
    
    def __init__(self, filename: str = "library.json"):
        """
        Library sınıfının constructor'ı.
        
        Args:
            filename (str): Kitapların saklanacağı JSON dosyasının adı
        """
        self.filename = filename
        self.books: List[Book] = []
        self.load_books()
    
    def add_book(self, book: Book) -> bool:
        """
        Kütüphaneye yeni bir kitap ekler.
        
        Args:
            book (Book): Eklenecek kitap nesnesi
            
        Returns:
            bool: Ekleme işlemi başarılıysa True, ISBN zaten varsa False
            
        Raises:
            ValueError: Kitap eklenirken bir hata oluştuğunda
        """
        try:
            # ISBN kontrolü - aynı ISBN'li kitap varsa ekleme
            if self.find_book(book.isbn):
                print(f"Hata: {book.isbn} ISBN'li kitap zaten mevcut")
                return False
            
            self.books.append(book)
            self.save_books()
            return True
            
        except Exception as e:
            # Log the error (in a real app, use proper logging)
            print(f"Hata: Kitap eklenirken bir hata oluştu: {str(e)}")
            raise
    
    def add_book_by_isbn(self, isbn: str) -> bool:
        """
        ISBN numarasına göre Open Library API'sinden kitap bilgilerini çeker ve ekler.
        
        Args:
            isbn (str): Eklenecek kitabın ISBN numarası
            
        Returns:
            bool: Ekleme işlemi başarılıysa True, hata varsa False
            
        Raises:
            ValueError: Geçersiz ISBN veya API'den veri çekilemediğinde
        """
        try:
            # ISBN kontrolü - aynı ISBN'li kitap varsa ekleme
            if self.find_book(isbn):
                raise ValueError(f"{isbn} ISBN'li kitap zaten mevcut")
            
            # Open Library API'sinden kitap bilgilerini çek
            book_data = self.fetch_book_from_api(isbn)
            if not book_data:
                raise ValueError("Kitap bilgileri alınamadı")
            
            # Yeni kitap oluştur ve ekle
            book = Book(
                title=book_data.get('title', 'Bilinmeyen Başlık'),
                author=book_data.get('author', 'Bilinmeyen Yazar'),
                isbn=isbn
            )
            
            self.books.append(book)
            self.save_books()
            return True
            
        except Exception as e:
            # Log the error (in a real app, use proper logging)
            print(f"Hata: ISBN ile kitap eklenirken bir hata oluştu: {str(e)}")
            raise
    
    def fetch_book_from_api(self, isbn: str) -> Optional[dict]:
        """
        Open Library API'sinden kitap bilgilerini çeker.
        
        Args:
            isbn (str): Aranacak kitabın ISBN numarası
            
        Returns:
            Optional[dict]: Kitap bilgileri veya None (hata durumunda)
            
        Raises:
            ValueError: API isteği başarısız olduğunda veya geçersiz yanıt alındığında
        """
        if not isbn or not isbn.strip():
            raise ValueError("Geçersiz ISBN numarası")
            
        try:
            # Open Library API URL'si
            url = f"https://openlibrary.org/isbn/{isbn}.json"
            
            # HTTP isteği gönder
            with httpx.Client(follow_redirects=True) as client:
                response = client.get(url, timeout=10.0)
                
                if response.status_code not in [200, 302]:
                    raise ValueError(f"API isteği başarısız oldu. Durum kodu: {response.status_code}")
                
                data = response.json()
                
                # Kitap başlığını al ve temizle
                title = str(data.get('title', 'Bilinmeyen Başlık')).strip()
                # HTML escaping Book sınıfında yapılacak, burada yapmıyoruz
                
                # Yazar bilgisini al
                author = 'Bilinmeyen Yazar'
                if 'authors' in data and data['authors']:
                    try:
                        # Yazar ID'sini al
                        author_id = data['authors'][0].get('key')
                        if author_id:
                            author_url = f"https://openlibrary.org{author_id}.json"
                            
                            # Yazar detaylarını getir
                            with httpx.Client(follow_redirects=True, timeout=5.0) as client:
                                author_response = client.get(author_url)
                                if author_response.status_code in [200, 302]:
                                    author_data = author_response.json()
                                    author_name = author_data.get('name')
                                    if author_name:
                                        author = str(author_name).strip()
                    except Exception as e:
                        # Hata durumunda varsayılan yazar adını kullan
                        print(f"Yazar bilgisi alınırken hata oluştu: {e}")
                
                return {
                    'title': title[:500],  # Maksimum 500 karakter
                    'author': author[:200],  # Maksimum 200 karakter
                    'isbn': isbn
                }
                
        except httpx.RequestError as e:
            error_msg = f"API isteği sırasında bir ağ hatası oluştu"
            print(f"{error_msg}: {str(e)}")
            raise ValueError(error_msg)
            
        except json.JSONDecodeError as e:
            error_msg = "API yanıtı geçersiz JSON formatında"
            print(f"{error_msg}: {str(e)}")
            raise ValueError(error_msg)
            
        except Exception as e:
            error_msg = f"Beklenmeyen bir hata oluştu: {type(e).__name__}"
            print(f"{error_msg}: {str(e)}")
            # Re-raise the original exception if it's already a ValueError
            if isinstance(e, ValueError):
                raise e
            raise ValueError("Kitap bilgileri alınırken bir hata oluştu")
    
    def fetch_author_from_api(self, author_key: str) -> Optional[str]:
        """
        Open Library API'sinden yazar bilgilerini çeker.
        
        Args:
            author_key (str): Yazarın API anahtarı (örn: /authors/OL23919A)
            
        Returns:
            Optional[str]: Yazar adı veya None
        """
        try:
            url = f"https://openlibrary.org{author_key}.json"
            
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('name', 'Bilinmeyen Yazar')
                
        except Exception:
            # Yazar bilgisi alınamazsa sessizce geç
            pass
        
        return None
    
    def remove_book(self, isbn: str) -> bool:
        """
        ISBN numarasına göre kitabı kütüphaneden siler.
        
        Args:
            isbn (str): Silinecek kitabın ISBN numarası
            
        Returns:
            bool: Silme işlemi başarılıysa True, kitap bulunamazsa False
        """
        book = self.find_book(isbn)
        if book:
            self.books.remove(book)
            self.save_books()
            print(f"Kitap başarıyla silindi: {book}")
            return True
        else:
            print(f"Hata: {isbn} ISBN'li kitap bulunamadı!")
            return False
    
    def list_books(self) -> None:
        """
        Kütüphanedeki tüm kitapları listeler.
        """
        if not self.books:
            print("Kütüphanede hiç kitap yok.")
            return
        
        print(f"\n=== Kütüphanedeki Kitaplar ({len(self.books)} adet) ===")
        for i, book in enumerate(self.books, 1):
            print(f"{i}. {book}")
        print()
    
    def find_book(self, isbn: str) -> Optional[Book]:
        """
        ISBN numarasına göre kitap arar.
        
        Args:
            isbn (str): Aranacak kitabın ISBN numarası
            
        Returns:
            Optional[Book]: Bulunan kitap nesnesi veya None
        """
        for book in self.books:
            if book.isbn == isbn:
                return book
        return None
    
    def search_books(self, query: str) -> List[Book]:
        """
        Başlık veya yazar adına göre kitap arar.
        
        Args:
            query (str): Arama sorgusu
            
        Returns:
            List[Book]: Bulunan kitapların listesi
        """
        query = query.lower()
        found_books = []
        
        for book in self.books:
            if (query in book.title.lower() or 
                query in book.author.lower() or 
                query in book.isbn):
                found_books.append(book)
        
        return found_books
    
    def load_books(self) -> None:
        """
        JSON dosyasından kitapları yükler.
        """
        if not os.path.exists(self.filename):
            print(f"Veri dosyası ({self.filename}) bulunamadı. Yeni bir kütüphane oluşturuluyor.")
            return
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.books = [Book.from_dict(book_data) for book_data in data]
                print(f"{len(self.books)} kitap başarıyla yüklendi.")
        except json.JSONDecodeError:
            print(f"Hata: {self.filename} dosyası bozuk. Yeni bir kütüphane oluşturuluyor.")
            self.books = []
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")
            self.books = []
    
    def save_books(self) -> None:
        """
        Kitapları JSON dosyasına kaydeder.
        """
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                books_data = [book.to_dict() for book in self.books]
                json.dump(books_data, file, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Dosya kaydetme hatası: {e}")
    
    def get_book_count(self) -> int:
        """
        Kütüphanedeki toplam kitap sayısını döndürür.
        
        Returns:
            int: Kitap sayısı
        """
        return len(self.books)
    
    def get_all_books(self) -> List[Book]:
        """
        Tüm kitapların listesini döndürür.
        
        Returns:
            List[Book]: Kitapların listesi
        """
        return self.books.copy()
