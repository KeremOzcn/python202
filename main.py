#!/usr/bin/env python3
"""
Kütüphane Yönetim Sistemi - Ana Uygulama
Global AI Hub Python 202 Bootcamp Projesi - Aşama 1
"""

from library import Library
from book import Book


def display_menu():
    """Ana menüyü ekrana yazdırır."""
    print("\n" + "="*50)
    print("    KÜTÜPHANE YÖNETİM SİSTEMİ")
    print("="*50)
    print("1. Kitap Ekle")
    print("2. Kitap Sil")
    print("3. Kitapları Listele")
    print("4. Kitap Ara")
    print("5. Kütüphane İstatistikleri")
    print("6. Çıkış")
    print("-"*50)


def get_user_choice():
    """Kullanıcıdan seçim alır ve doğrular."""
    while True:
        try:
            choice = input("Seçiminizi yapın (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            else:
                print("Geçersiz seçim! Lütfen 1-6 arasında bir sayı girin.")
        except KeyboardInterrupt:
            print("\n\nProgram sonlandırılıyor...")
            return '6'


def add_book_menu(library: Library):
    """Kitap ekleme menüsü."""
    print("\n--- Kitap Ekleme ---")
    print("1. ISBN ile otomatik ekleme (Open Library API)")
    print("2. Manuel kitap ekleme")
    
    try:
        choice = input("Seçiminizi yapın (1-2): ").strip()
        
        if choice == '1':
            # API ile otomatik ekleme
            isbn = input("ISBN numarası: ").strip()
            if not isbn:
                print("Hata: ISBN numarası boş olamaz!")
                return
            
            print("Kitap bilgileri Open Library'den çekiliyor...")
            try:
                if library.add_book_by_isbn(isbn):
                    print(f"Kitap başarıyla eklendi.")
            except ValueError as e:
                # The library method already prints a detailed error, 
                # so we just inform the user that the operation failed.
                print(f"Hata: Kitap eklenemedi. {e}")
            
        elif choice == '2':
            # Manuel ekleme
            title = input("Kitap başlığı: ").strip()
            if not title:
                print("Hata: Kitap başlığı boş olamaz!")
                return
            
            author = input("Yazar adı: ").strip()
            if not author:
                print("Hata: Yazar adı boş olamaz!")
                return
            
            isbn = input("ISBN numarası: ").strip()
            if not isbn:
                print("Hata: ISBN numarası boş olamaz!")
                return
            
            # Yeni kitap oluştur ve ekle
            new_book = Book(title, author, isbn)
            library.add_book(new_book)
        
        else:
            print("Geçersiz seçim!")
        
    except KeyboardInterrupt:
        print("\nKitap ekleme iptal edildi.")


def remove_book_menu(library: Library):
    """Kitap silme menüsü."""
    print("\n--- Kitap Silme ---")
    
    if library.get_book_count() == 0:
        print("Kütüphanede silinecek kitap yok.")
        return
    
    try:
        isbn = input("Silinecek kitabın ISBN numarası: ").strip()
        if not isbn:
            print("Hata: ISBN numarası boş olamaz!")
            return
        
        # Önce kitabı göster
        book = library.find_book(isbn)
        if book:
            print(f"Silinecek kitap: {book}")
            confirm = input("Bu kitabı silmek istediğinizden emin misiniz? (e/h): ").strip().lower()
            if confirm in ['e', 'evet', 'yes', 'y']:
                library.remove_book(isbn)
            else:
                print("Silme işlemi iptal edildi.")
        else:
            print(f"Hata: {isbn} ISBN'li kitap bulunamadı!")
            
    except KeyboardInterrupt:
        print("\nKitap silme iptal edildi.")


def search_book_menu(library: Library):
    """Kitap arama menüsü."""
    print("\n--- Kitap Arama ---")
    
    if library.get_book_count() == 0:
        print("Kütüphanede aranacak kitap yok.")
        return
    
    try:
        print("Arama seçenekleri:")
        print("1. ISBN ile ara")
        print("2. Başlık/Yazar ile ara")
        
        search_type = input("Arama türünü seçin (1-2): ").strip()
        
        if search_type == '1':
            isbn = input("ISBN numarası: ").strip()
            if isbn:
                book = library.find_book(isbn)
                if book:
                    print(f"\nBulunan kitap: {book}")
                else:
                    print(f"'{isbn}' ISBN'li kitap bulunamadı.")
        
        elif search_type == '2':
            query = input("Başlık veya yazar adı: ").strip()
            if query:
                found_books = library.search_books(query)
                if found_books:
                    print(f"\n'{query}' için bulunan kitaplar ({len(found_books)} adet):")
                    for i, book in enumerate(found_books, 1):
                        print(f"{i}. {book}")
                else:
                    print(f"'{query}' için kitap bulunamadı.")
        else:
            print("Geçersiz arama türü!")
            
    except KeyboardInterrupt:
        print("\nArama iptal edildi.")


def show_statistics(library: Library):
    """Kütüphane istatistiklerini gösterir."""
    print("\n--- Kütüphane İstatistikleri ---")
    
    book_count = library.get_book_count()
    print(f"Toplam kitap sayısı: {book_count}")
    
    if book_count > 0:
        # Yazarlara göre grupla
        authors = {}
        for book in library.get_all_books():
            if book.author in authors:
                authors[book.author] += 1
            else:
                authors[book.author] = 1
        
        print(f"Farklı yazar sayısı: {len(authors)}")
        
        # En çok kitabı olan yazar
        if authors:
            max_author = max(authors, key=authors.get)
            max_count = authors[max_author]
            print(f"En çok kitabı olan yazar: {max_author} ({max_count} kitap)")


def main():
    """Ana program döngüsü."""
    print("Kütüphane Yönetim Sistemi'ne Hoş Geldiniz!")
    
    # Kütüphane nesnesini oluştur
    library = Library()
    
    while True:
        display_menu()
        choice = get_user_choice()
        
        if choice == '1':
            add_book_menu(library)
        
        elif choice == '2':
            remove_book_menu(library)
        
        elif choice == '3':
            print("\n--- Kitap Listesi ---")
            library.list_books()
        
        elif choice == '4':
            search_book_menu(library)
        
        elif choice == '5':
            show_statistics(library)
        
        elif choice == '6':
            print("\nKütüphane Yönetim Sistemi kapatılıyor...")
            print("Görüşmek üzere!")
            break
        
        # Devam etmek için kullanıcıdan onay al
        if choice != '6':
            input("\nDevam etmek için Enter tuşuna basın...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından sonlandırıldı.")
    except Exception as e:
        print(f"\nBeklenmeyen bir hata oluştu: {e}")
        print("Program sonlandırılıyor...")
