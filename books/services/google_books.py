import requests
import time
from typing import Optional, Dict, Any
from django.conf import settings


class GoogleBooksAPI:
    """Класс для работы с Google Books API"""

    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    @staticmethod
    def search_books(query: str, max_results: int = 10) -> Optional[Dict[str, Any]]:
        """
        Поиск книг по запросу

        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов

        Returns:
            Словарь с результатами поиска или None в случае ошибки
        """
        params = {
            'q': query,
            'maxResults': max_results,
            'langRestrict': 'ru',
        }

        try:
            response = requests.get(GoogleBooksAPI.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при запросе к Google Books API: {e}")
            return None

    @staticmethod
    def get_book_by_isbn(isbn: str) -> Optional[Dict[str, Any]]:
        """
        Получение информации о книге по ISBN

        Args:
            isbn: ISBN книги

        Returns:
            Словарь с информацией о книге или None
        """
        query = f"isbn:{isbn}"
        data = GoogleBooksAPI.search_books(query, max_results=1)

        if data and data.get('totalItems', 0) > 0:
            return data['items'][0]
        return None

    @staticmethod
    def extract_book_data(api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлечение и форматирование данных о книге из ответа API

        Args:
            api_data: Данные от API

        Returns:
            Отформатированный словарь с данными о книге
        """
        volume_info = api_data.get('volumeInfo', {})
        
        isbn_13 = None
        isbn_10 = None
        for identifier in volume_info.get('industryIdentifiers', []):
            if identifier.get('type') == 'ISBN_13':
                isbn_13 = identifier.get('identifier')
            elif identifier.get('type') == 'ISBN_10':
                isbn_10 = identifier.get('identifier')
        
        description = volume_info.get('description', '')
        if description and len(description) > 2000:
            description = description[:2000] + '...'

        image_links = volume_info.get('imageLinks', {})
        cover_url = None
        for size in ['extraLarge', 'large', 'medium', 'small', 'thumbnail']:
            if size in image_links:
                cover_url = image_links[size]
                break

        page_count = volume_info.get('pageCount')
        if page_count and page_count > 1000:
            page_count = None

        language = volume_info.get('language', '')
        if language not in ['ru', 'en']: 
            language = 'ru'  

        return {
            'google_books_id': api_data.get('id'),
            'title': volume_info.get('title', 'Неизвестно'),
            'author': ', '.join(volume_info.get('authors', ['Неизвестный автор'])),
            'isbn': isbn_13 or isbn_10 or '',
            'description': description,
            'published_date': volume_info.get('publishedDate', ''),
            'publisher': volume_info.get('publisher', ''),
            'page_count': page_count,
            'language': language,
            'cover_url': cover_url,
            'average_rating': volume_info.get('averageRating', 0),
            'ratings_count': volume_info.get('ratingsCount', 0),
            'categories': volume_info.get('categories', []),
        }

    @staticmethod
    def estimate_book_parameters(api_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Оценка параметров книги на основе данных API

        Args:
            api_data: Данные от API

        Returns:
            Словарь с оцененными параметрами
        """
        volume_info = api_data.get('volumeInfo', {})

      
        page_count = volume_info.get('pageCount', 300)
        if page_count < 150:
            pace = 4  
        elif page_count < 350:
            pace = 3  
        else:
            pace = 2  
            
        
        categories = volume_info.get('categories', [])
        description = volume_info.get('description', '').lower()

        complexity_keywords = {
            'научный': 5, 'философия': 5, 'исследование': 4,
            'роман': 3, 'повесть': 3, 'рассказ': 2,
            'детектив': 3, 'фэнтези': 3, 'фантастика': 3,
            'саморазвитие': 2, 'психология': 4, 'история': 4
        }

        complexity = 3  
        for category in categories:
            category_lower = category.lower()
            for keyword, score in complexity_keywords.items():
                if keyword in category_lower:
                    complexity = score
                    break

        
        emotional_keywords = {
            'драма': 5, 'трагедия': 5, 'романтика': 4,
            'комедия': 3, 'приключения': 4, 'ужасы': 5,
            'мистика': 4, 'детектив': 3, 'биография': 3
        }

        emotional_intensity = 3  
        for category in categories:
            category_lower = category.lower()
            for keyword, score in emotional_keywords.items():
                if keyword in category_lower:
                    emotional_intensity = score
                    break

        return {
            'pace': pace,
            'complexity': complexity,
            'emotional_intensity': emotional_intensity
        }


class BookImporter:
    """Класс для импорта книг из Google Books API"""

    @staticmethod
    def import_book_by_isbn(isbn: str) -> Optional[Dict[str, Any]]:
        """
        Импорт книги по ISBN

        Args:
            isbn: ISBN книги

        Returns:
            Словарь с результатами импорта или None
        """
        
        from books.models import Book
        if Book.objects.filter(isbn=isbn).exists():
            return {'success': False, 'message': 'Книга с таким ISBN уже существует'}

        
        api_data = GoogleBooksAPI.get_book_by_isbn(isbn)
        if not api_data:
            return {'success': False, 'message': 'Книга не найдена в Google Books'}

        
        book_data = GoogleBooksAPI.extract_book_data(api_data)
        estimated_params = GoogleBooksAPI.estimate_book_parameters(api_data)

        
        book_data.update(estimated_params)

        return {
            'success': True,
            'message': 'Книга найдена в Google Books',
            'book_data': book_data
        }