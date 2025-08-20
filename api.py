#!/usr/bin/env python3
"""
Kütüphane Yönetim Sistemi - FastAPI Web Servisi
Global AI Hub Python 202 Bootcamp Projesi - Aşama 3
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional
import re
import html
from library import Library
from book import Book

# FastAPI uygulaması oluştur
app = FastAPI(
    title="Kütüphane Yönetim Sistemi API",
    description="Global AI Hub Python 202 Bootcamp Projesi - Kitap yönetimi için REST API",
    version="1.0.0"
)

# Global kütüphane nesnesi
library = Library("api_library.json")


# Pydantic modelleri
class BookResponse(BaseModel):
    """API'nin döndüreceği kitap modeli."""
    title: str
    author: str
    isbn: str
    
    class Config:
        from_attributes = True


class BookCreate(BaseModel):
    """Kitap oluşturma için model."""
    title: str
    author: str
    isbn: str
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Başlık boş olamaz')
        # HTML escape ve uzunluk kontrolü
        v = html.escape(v.strip())
        if len(v) > 500:
            raise ValueError('Başlık çok uzun (max 500 karakter)')
        return v
    
    @validator('author')
    def validate_author(cls, v):
        if not v or not v.strip():
            raise ValueError('Yazar adı boş olamaz')
        # HTML escape ve uzunluk kontrolü
        v = html.escape(v.strip())
        if len(v) > 200:
            raise ValueError('Yazar adı çok uzun (max 200 karakter)')
        return v
    
    @validator('isbn')
    def validate_isbn(cls, v):
        if not v or not v.strip():
            raise ValueError('ISBN boş olamaz')
        # ISBN formatı kontrolü (sadece rakam ve tire)
        v = v.strip()
        if not re.match(r'^[\d\-X]+$', v):
            raise ValueError('Geçersiz ISBN formatı')
        if len(v) > 20:
            raise ValueError('ISBN çok uzun')
        return v


class ISBNRequest(BaseModel):
    """ISBN ile kitap ekleme için model."""
    isbn: str
    
    @validator('isbn')
    def validate_isbn(cls, v):
        if not v or not v.strip():
            raise ValueError('ISBN boş olamaz')
        # ISBN formatı kontrolü
        v = v.strip()
        if not re.match(r'^[\d\-X]+$', v):
            raise ValueError('Geçersiz ISBN formatı')
        if len(v) > 20:
            raise ValueError('ISBN çok uzun')
        return v


class MessageResponse(BaseModel):
    """Genel mesaj yanıtı modeli."""
    message: str
    success: bool


# API Endpoint'leri

@app.get("/", response_model=dict)
async def root():
    """Ana sayfa - API bilgileri."""
    return {
        "message": "Kütüphane Yönetim Sistemi API",
        "version": "1.0.0",
        "endpoints": {
            "GET /books": "Tüm kitapları listele",
            "POST /books": "ISBN ile kitap ekle (Open Library API)",
            "POST /books/manual": "Manuel kitap ekle",
            "DELETE /books/{isbn}": "Kitap sil",
            "GET /books/{isbn}": "Belirli bir kitabı getir",
            "GET /books/search/{query}": "Kitap ara",
            "GET /stats": "Kütüphane istatistikleri"
        }
    }


@app.get("/books", response_model=List[BookResponse])
async def get_all_books():
    """Kütüphanedeki tüm kitapları döndürür."""
    books = library.get_all_books()
    return [BookResponse(title=book.title, author=book.author, isbn=book.isbn) for book in books]


@app.post("/books", response_model=BookResponse)
async def add_book_by_isbn(isbn_request: ISBNRequest):
    """
    ISBN numarasına göre Open Library API'sinden kitap bilgilerini çeker ve ekler.
    """
    isbn = isbn_request.isbn.strip()
    
    if not isbn:
        raise HTTPException(status_code=400, detail="ISBN numarası boş olamaz")
    
    # ISBN zaten var mı kontrol et
    if library.find_book(isbn):
        raise HTTPException(status_code=409, detail=f"ISBN {isbn} zaten mevcut")
    
    # API'den kitap bilgilerini çek
    success = library.add_book_by_isbn(isbn)
    
    if not success:
        raise HTTPException(status_code=404, detail="Kitap Open Library'de bulunamadı veya API hatası")
    
    # Eklenen kitabı döndür
    added_book = library.find_book(isbn)
    return BookResponse(title=added_book.title, author=added_book.author, isbn=added_book.isbn)


@app.post("/books/manual", response_model=BookResponse)
async def add_book_manual(book_data: BookCreate):
    """
    Manuel olarak kitap ekler.
    """
    # Veri doğrulama
    if not book_data.title.strip():
        raise HTTPException(status_code=400, detail="Kitap başlığı boş olamaz")
    
    if not book_data.author.strip():
        raise HTTPException(status_code=400, detail="Yazar adı boş olamaz")
    
    if not book_data.isbn.strip():
        raise HTTPException(status_code=400, detail="ISBN numarası boş olamaz")
    
    # ISBN zaten var mı kontrol et
    if library.find_book(book_data.isbn):
        raise HTTPException(status_code=409, detail=f"ISBN {book_data.isbn} zaten mevcut")
    
    # Kitap oluştur ve ekle
    new_book = Book(book_data.title, book_data.author, book_data.isbn)
    success = library.add_book(new_book)
    
    if not success:
        raise HTTPException(status_code=500, detail="Kitap eklenirken hata oluştu")
    
    return BookResponse(title=new_book.title, author=new_book.author, isbn=new_book.isbn)


@app.get("/books/{isbn}", response_model=BookResponse)
async def get_book_by_isbn(isbn: str):
    """
    Belirli bir ISBN'e sahip kitabı döndürür.
    """
    # Güvenlik: ISBN sanitizasyonu
    isbn = isbn.strip()
    if not re.match(r'^[\d\-X]+$', isbn) or len(isbn) > 20:
        raise HTTPException(status_code=400, detail="Geçersiz ISBN formatı")
    
    book = library.find_book(isbn)
    
    if not book:
        raise HTTPException(status_code=404, detail=f"ISBN {isbn} bulunamadı")
    
    return BookResponse(title=book.title, author=book.author, isbn=book.isbn)


@app.delete("/books/{isbn}", response_model=MessageResponse)
async def delete_book(isbn: str):
    """
    Belirtilen ISBN'e sahip kitabı siler.
    """
    # Güvenlik: ISBN sanitizasyonu
    isbn = isbn.strip()
    if not re.match(r'^[\d\-X]+$', isbn) or len(isbn) > 20:
        raise HTTPException(status_code=400, detail="Geçersiz ISBN formatı")
    
    success = library.remove_book(isbn)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"ISBN {isbn} bulunamadı")
    
    return MessageResponse(message=f"ISBN {isbn} başarıyla silindi", success=True)


@app.get("/books/search/{query}", response_model=List[BookResponse])
async def search_books(query: str):
    """
    Başlık, yazar veya ISBN'e göre kitap arar.
    """
    # Güvenlik: Query sanitizasyonu
    query = query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Arama sorgusu boş olamaz")
    
    # Uzunluk kontrolü
    if len(query) > 100:
        raise HTTPException(status_code=400, detail="Arama sorgusu çok uzun")
    
    # HTML escape
    query = html.escape(query)
    
    found_books = library.search_books(query)
    
    return [BookResponse(title=book.title, author=book.author, isbn=book.isbn) for book in found_books]


@app.get("/stats", response_model=dict)
async def get_library_stats():
    """
    Kütüphane istatistiklerini döndürür.
    """
    books = library.get_all_books()
    book_count = len(books)
    
    # Yazarlara göre grupla
    authors = {}
    for book in books:
        if book.author in authors:
            authors[book.author] += 1
        else:
            authors[book.author] = 1
    
    stats = {
        "total_books": book_count,
        "unique_authors": len(authors),
        "authors_with_most_books": None,
        "most_books_count": 0
    }
    
    if authors:
        max_author = max(authors, key=authors.get)
        stats["authors_with_most_books"] = max_author
        stats["most_books_count"] = authors[max_author]
    
    return stats


# Güvenli hata yakalama middleware'i
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Genel hata yakalayıcı - güvenli hata mesajları."""
    # Güvenlik: Detaylı hata bilgilerini logla ama kullanıcıya gösterme
    import logging
    logging.error(f"API Hatası: {str(exc)}")
    
    # Kullanıcıya sadece genel hata mesajı döndür
    return HTTPException(status_code=500, detail="Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.")


if __name__ == "__main__":
    import uvicorn
    print("Kütüphane Yönetim Sistemi API başlatılıyor...")
    print("API dokümantasyonu: http://localhost:8000/docs")
    print("Alternatif dokümantasyon: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
