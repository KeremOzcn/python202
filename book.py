import re
import html
from typing import Optional


class Book:
    """
    Bir kitabı temsil eden sınıf.
    
    Attributes:
        title (str): Kitabın başlığı
        author (str): Kitabın yazarı
        isbn (str): Kitabın benzersiz ISBN numarası
    """
    
    def __init__(self, title: str, author: str, isbn: str):
        """
        Book sınıfının constructor'ı.
        
        Args:
            title (str): Kitabın başlığı (1-500 karakter)
            author (str): Kitabın yazarı (1-200 karakter)
            isbn (str): Kitabın ISBN numarası (1-20 karakter, sadece rakam ve tire)
            
        Raises:
            ValueError: Geçersiz giriş değerleri için
        """
        self.title = self._validate_title(title)
        self.author = self._validate_author(author)
        self.isbn = self._validate_isbn(isbn)
        
    @staticmethod
    def _validate_title(title: str) -> str:
        """Kitap başlığını doğrular ve temizler."""
        if not title or not title.strip():
            raise ValueError('Kitap başlığı boş olamaz')
        
        title = html.escape(title.strip())
        if len(title) > 500:
            raise ValueError('Kitap başlığı çok uzun (maksimum 500 karakter)')
            
        return title
        
    @staticmethod
    def _validate_author(author: str) -> str:
        """Yazar adını doğrular ve temizler."""
        if not author or not author.strip():
            raise ValueError('Yazar adı boş olamaz')
            
        author = html.escape(author.strip())
        if len(author) > 200:
            raise ValueError('Yazar adı çok uzun (maksimum 200 karakter)')
            
        return author
        
    @staticmethod
    def _validate_isbn(isbn: str) -> str:
        """ISBN numarasını doğrular ve temizler."""
        if not isbn or not isbn.strip():
            raise ValueError('ISBN boş olamaz')
            
        isbn = isbn.strip()
        if not re.match(r'^[\d\-X]+$', isbn):
            raise ValueError('Geçersiz ISBN formatı (sadece rakam ve tire içerebilir)')
            
        if len(isbn) > 20:
            raise ValueError('ISBN çok uzun (maksimum 20 karakter)')
            
        return isbn
    
    def __str__(self) -> str:
        """
        Kitabın string temsilini döndürür.
        
        Returns:
            str: "Başlık by Yazar (ISBN: isbn_numarası)" formatında string
        """
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"
    
    def __repr__(self) -> str:
        """
        Kitabın resmi string temsilini döndürür.
        
        Returns:
            str: Book nesnesinin resmi temsili
        """
        return f"Book(title='{self.title}', author='{self.author}', isbn='{self.isbn}')"
    
    def to_dict(self) -> dict:
        """
        Book nesnesini dictionary'ye çevirir (JSON serileştirme için).
        
        Returns:
            dict: Kitap bilgilerini içeren dictionary
        """
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Book':
        """
        Dictionary'den Book nesnesi oluşturur (JSON deserileştirme için).
        
        Args:
            data (dict): Kitap bilgilerini içeren dictionary
            
        Returns:
            Book: Oluşturulan Book nesnesi
        """
        return cls(
            title=data["title"],
            author=data["author"],
            isbn=data["isbn"]
        )
