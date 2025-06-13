from src.models import Author, Book
from src.repositories import AuthorRepository, BookRepository

class UserInterface:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def display_menu(self):
        """Display the main menu."""
        print("\n=== System Zarządzania Biblioteką Domową ===")
        print("1. Zarządzanie autorami")
        print("2. Zarządzanie książkami")
        print("3. Raporty i statystyki")
        print("0. Wyjście")
        return input("Wybierz opcję: ")
    
    def display_authors_menu(self):
        """Display the authors management menu."""
        print("\n=== Zarządzanie autorami ===")
        print("1. Dodaj nowego autora")
        print("2. Wyświetl wszystkich autorów")
        print("3. Wyszukaj autora")
        print("4. Edytuj autora")
        print("5. Usuń autora")
        print("0. Powrót")
        return input("Wybierz opcję: ")
    
    def display_books_menu(self):
        """Display the books management menu."""
        print("\n=== Zarządzanie książkami ===")
        print("1. Dodaj nową książkę")
        print("2. Wyświetl wszystkie książki")
        print("3. Wyszukaj książkę")
        print("4. Edytuj książkę")
        print("5. Usuń książkę")
        print("6. Wyświetl książki autora")
        print("0. Powrót")
        return input("Wybierz opcję: ")
    
    def get_author_data(self):
        """Get author data from user input."""
        first_name = input("Imię: ")
        last_name = input("Nazwisko: ")
        birth_year = input("Rok urodzenia (opcjonalnie): ")
        nationality = input("Narodowość (opcjonalnie): ")
        
        author = Author(
            first_name=first_name,
            last_name=last_name,
            birth_year=int(birth_year) if birth_year.isdigit() else None,
            nationality=nationality if nationality else None
        )
        return author
    
    def get_book_data(self, author_repo):
        """Get book data from user input."""
        title = input("Tytuł: ")
        
        # Display authors for selection
        authors = author_repo.get_all()
        print("\nDostępni autorzy:")
        for author in authors:
            print(f"{author.id}. {author.first_name} {author.last_name}")
        
        author_id = int(input("Wybierz ID autora: "))
        publication_year = input("Rok wydania (opcjonalnie): ")
        genre = input("Gatunek (opcjonalnie): ")
        pages = input("Liczba stron (opcjonalnie): ")
        description = input("Opis (opcjonalnie): ")
        
        book = Book(
            title=title,
            author_id=author_id,
            publication_year=int(publication_year) if publication_year.isdigit() else None,
            genre=genre if genre else None,
            pages=int(pages) if pages.isdigit() else None,
            description=description if description else None
        )
        return book
    
    def display_author(self, author):
        """Display author information."""
        print(f"\nID: {author.id}")
        print(f"Imię: {author.first_name}")
        print(f"Nazwisko: {author.last_name}")
        if author.birth_year:
            print(f"Rok urodzenia: {author.birth_year}")
        if author.nationality:
            print(f"Narodowość: {author.nationality}")
    
    def display_book(self, book):
        """Display book information."""
        print(f"\nID: {book.id}")
        print(f"Tytuł: {book.title}")
        print(f"Autor: {book.author.first_name} {book.author.last_name}")
        if book.publication_year:
            print(f"Rok wydania: {book.publication_year}")
        if book.genre:
            print(f"Gatunek: {book.genre}")
        if book.pages:
            print(f"Liczba stron: {book.pages}")
        if book.description:
            print(f"Opis: {book.description}")
    
    def display_statistics(self, stats):
        """Display library statistics."""
        print("\n=== Statystyki biblioteki ===")
        print(f"Liczba książek: {stats['total_books']}")
        print(f"Liczba autorów: {stats['total_authors']}")
        
        if stats['oldest_book']:
            print(f"\nNajstarsza książka: {stats['oldest_book'].title} ({stats['oldest_book'].publication_year})")
        if stats['newest_book']:
            print(f"Najnowsza książka: {stats['newest_book'].title} ({stats['newest_book'].publication_year})")
        
        print("\nAutorzy z książkami:")
        for author, _ in stats['authors_with_books']:
            print(f"- {author.first_name} {author.last_name}")
    
    def run(self):
        """Run the main application loop."""
        while True:
            choice = self.display_menu()
            
            if choice == "0":
                break
            elif choice == "1":
                self.handle_authors()
            elif choice == "2":
                self.handle_books()
            elif choice == "3":
                self.handle_statistics()
            else:
                print("Nieprawidłowy wybór!")
    
    def handle_authors(self):
        """Handle author management operations."""
        with self.db_manager.get_session() as session:
            author_repo = AuthorRepository(session)
            
            while True:
                choice = self.display_authors_menu()
                
                if choice == "0":
                    break
                elif choice == "1":
                    author = self.get_author_data()
                    author_repo.add(author)
                    print("Autor dodany pomyślnie!")
                elif choice == "2":
                    authors = author_repo.get_all()
                    for author in authors:
                        self.display_author(author)
                elif choice == "3":
                    name = input("Wprowadź imię lub nazwisko: ")
                    authors = author_repo.search_by_name(name)
                    for author in authors:
                        self.display_author(author)
                elif choice == "4":
                    author_id = int(input("Wprowadź ID autora do edycji: "))
                    author = author_repo.get_by_id(author_id)
                    if author:
                        print("\nAktualne dane:")
                        self.display_author(author)
                        print("\nWprowadź nowe dane:")
                        updated_author = self.get_author_data()
                        updated_author.id = author_id
                        author_repo.update(updated_author)
                        print("Autor zaktualizowany pomyślnie!")
                    else:
                        print("Nie znaleziono autora!")
                elif choice == "5":
                    author_id = int(input("Wprowadź ID autora do usunięcia: "))
                    if author_repo.delete(author_id):
                        print("Autor usunięty pomyślnie!")
                    else:
                        print("Nie można usunąć autora - ma przypisane książki lub nie istnieje!")
                else:
                    print("Nieprawidłowy wybór!")
    
    def handle_books(self):
        """Handle book management operations."""
        with self.db_manager.get_session() as session:
            author_repo = AuthorRepository(session)
            book_repo = BookRepository(session)
            
            while True:
                choice = self.display_books_menu()
                
                if choice == "0":
                    break
                elif choice == "1":
                    book = self.get_book_data(author_repo)
                    book_repo.add(book)
                    print("Książka dodana pomyślnie!")
                elif choice == "2":
                    books = book_repo.get_all()
                    for book in books:
                        self.display_book(book)
                elif choice == "3":
                    query = input("Wprowadź tytuł, autora lub rok wydania: ")
                    books = book_repo.search(query)
                    for book in books:
                        self.display_book(book)
                elif choice == "4":
                    book_id = int(input("Wprowadź ID książki do edycji: "))
                    book = book_repo.get_by_id(book_id)
                    if book:
                        print("\nAktualne dane:")
                        self.display_book(book)
                        print("\nWprowadź nowe dane:")
                        updated_book = self.get_book_data(author_repo)
                        updated_book.id = book_id
                        book_repo.update(updated_book)
                        print("Książka zaktualizowana pomyślnie!")
                    else:
                        print("Nie znaleziono książki!")
                elif choice == "5":
                    book_id = int(input("Wprowadź ID książki do usunięcia: "))
                    if book_repo.delete(book_id):
                        print("Książka usunięta pomyślnie!")
                    else:
                        print("Nie znaleziono książki!")
                elif choice == "6":
                    author_id = int(input("Wprowadź ID autora: "))
                    books = book_repo.get_by_author(author_id)
                    for book in books:
                        self.display_book(book)
                else:
                    print("Nieprawidłowy wybór!")
    
    def handle_statistics(self):
        """Handle library statistics."""
        with self.db_manager.get_session() as session:
            book_repo = BookRepository(session)
            stats = book_repo.get_statistics()
            self.display_statistics(stats) 