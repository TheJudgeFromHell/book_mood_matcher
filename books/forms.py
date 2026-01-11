from django import forms
from .models import Book, Genre, MoodTag
from .services.google_books import BookImporter


class BookImportForm(forms.Form):
    """Форма для импорта книг по ISBN"""
    isbn = forms.CharField(
        max_length=20,
        label='ISBN книги',
        help_text='Введите ISBN-13 или ISBN-10'
    )

    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        label='Жанр',
        required=True
    )

    mood_tags = forms.ModelMultipleChoiceField(
        queryset=MoodTag.objects.all(),
        label='Теги настроения',
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def clean_isbn(self):
        """Валидация ISBN"""
        isbn = self.cleaned_data['isbn']

        isbn = isbn.replace('-', '').replace(' ', '')

        if not isbn.isdigit():
            raise forms.ValidationError('ISBN должен содержать только цифры')


        if len(isbn) not in [10, 13]:
            raise forms.ValidationError('ISBN должен содержать 10 или 13 цифр')

        return isbn

    def import_book(self):
        """Импорт книги по ISBN"""
        isbn = self.cleaned_data['isbn']
        genre = self.cleaned_data['genre']
        mood_tags = self.cleaned_data['mood_tags']


        result = BookImporter.import_book_by_isbn(isbn)

        if result['success']:
            book_data = result['book_data']


            book = Book.objects.create(
                title=book_data['title'],
                author=book_data['author'],
                isbn=isbn,
                description=book_data['description'],
                genre=genre,
                pace=book_data['pace'],
                complexity=book_data['complexity'],
                emotional_intensity=book_data['emotional_intensity'],
                page_count=book_data['page_count'],
                cover_url=book_data['cover_url'],
                google_books_id=book_data['google_books_id'],
                published_date=book_data['published_date'],
                publisher=book_data['publisher'],
                language=book_data['language'],
                average_rating=book_data['average_rating'],
                ratings_count=book_data['ratings_count'],
            )


            if mood_tags:
                book.mood_tags.set(mood_tags)

            return {
                'success': True,
                'message': f'Книга "{book.title}" успешно импортирована!',
                'book': book
            }
        else:
            return result