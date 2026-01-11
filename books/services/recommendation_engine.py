import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from django.db.models import Q
from ..models import Book, MoodTag, ReadingSession


class RecommendationEngine:
    """Движок рекомендаций книг"""

    def __init__(self):
        self.books_df = None
        self._load_books_data()

    def _load_books_data(self):
        """Загрузка данных о книгах в DataFrame"""
        books = Book.objects.filter(is_active=True).select_related('genre').prefetch_related('mood_tags')

        data = []
        for book in books:
            data.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'genre_id': book.genre.id,
                'genre_name': book.genre.name,
                'pace': book.pace,
                'complexity': book.complexity,
                'emotional_intensity': book.emotional_intensity,
                'page_count': book.page_count,
                'mood_tags': [tag.id for tag in book.mood_tags.all()],
                'mood_tag_names': [tag.name for tag in book.mood_tags.all()],
                'average_rating': book.average_rating,
            })

        self.books_df = pd.DataFrame(data)

    def recommend_books(
            self,
            session: ReadingSession,
            max_recommendations: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Рекомендация книг на основе сессии чтения

        Args:
            session: Сессия чтения с параметрами пользователя
            max_recommendations: Максимальное количество рекомендаций

        Returns:
            Список рекомендованных книг с оценками релевантности
        """
        if self.books_df.empty:
            return []


        user_vector = self._create_user_vector(session)


        recommendations = []
        for _, book_row in self.books_df.iterrows():
            book_vector = self._create_book_vector(book_row)
            relevance_score = self._calculate_relevance(user_vector, book_vector, session)

            if relevance_score > 0.3:
                recommendations.append({
                    'book_id': book_row['id'],
                    'relevance_score': relevance_score,
                    'match_reasons': self._get_match_reasons(user_vector, book_vector, session)
                })


        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        top_recommendations = recommendations[:max_recommendations]

        return top_recommendations

    def _create_user_vector(self, session: ReadingSession) -> Dict[str, float]:
        """Создание вектора пользовательских предпочтений"""

        energy_mapping = {'low': 1, 'medium': 2, 'high': 3}


        time_mapping = {15: 1, 30: 2, 60: 3, 90: 4, 120: 5}

        user_vector = {
            'energy_level': energy_mapping.get(session.energy_level, 2),
            'time_available': time_mapping.get(session.time_available, 2),
            'selected_tag_ids': [tag.id for tag in session.selected_mood_tags.all()],
        }

        return user_vector

    def _create_book_vector(self, book_row: pd.Series) -> Dict[str, Any]:
        """Создание вектора книги"""
        return {
            'pace': book_row['pace'],
            'complexity': book_row['complexity'],
            'emotional_intensity': book_row['emotional_intensity'],
            'page_count': book_row['page_count'],
            'mood_tags': book_row['mood_tags'],
            'genre_id': book_row['genre_id'],
            'average_rating': book_row['average_rating'],
        }

    def _calculate_relevance(
            self,
            user_vector: Dict[str, float],
            book_vector: Dict[str, Any],
            session: ReadingSession
    ) -> float:
        """
        Расчет релевантности книги для пользователя

        Возвращает значение от 0 до 1
        """
        score = 0
        weights = {
            'pace_time_match': 0.3,
            'complexity_energy_match': 0.25,
            'mood_tags_match': 0.25,
            'rating_boost': 0.2,
        }


        time_available = user_vector['time_available']
        book_pace = book_vector['pace']

        if time_available <= 2:
            pace_score = (book_pace - 3) / 2
        else:
            pace_score = 1 - abs(book_pace - 3) / 2

        score += max(0, pace_score) * weights['pace_time_match']


        user_energy = user_vector['energy_level']
        book_complexity = book_vector['complexity']

        if user_energy == 1:
            complexity_score = (3 - book_complexity) / 2
        elif user_energy == 3:
            complexity_score = (book_complexity - 2) / 3
        else:
            complexity_score = 1 - abs(book_complexity - 3) / 2

        score += max(0, complexity_score) * weights['complexity_energy_match']


        user_tags = set(user_vector['selected_tag_ids'])
        book_tags = set(book_vector['mood_tags'])

        if user_tags:
            tag_match_score = len(user_tags & book_tags) / len(user_tags)
        else:

            tag_match_score = 0.5

        score += tag_match_score * weights['mood_tags_match']


        rating_score = min(book_vector['average_rating'] / 5, 1)
        score += rating_score * weights['rating_boost']


        return max(0, min(1, score))

    def _get_match_reasons(
            self,
            user_vector: Dict[str, float],
            book_vector: Dict[str, Any],
            session: ReadingSession
    ) -> List[str]:
        """Формирование списка причин рекомендации"""
        reasons = []


        time_available = session.get_time_available_display()
        book_pace = book_vector['pace']

        if book_pace >= 4 and session.time_available <= 30:
            reasons.append(f"Быстрый темп чтения подходит для {time_available}")
        elif book_pace <= 2 and session.time_available >= 60:
            reasons.append(f"Неторопливый темп подходит для длительного чтения")


        if book_vector['complexity'] <= 2 and session.energy_level == 'low':
            reasons.append("Небольшая сложность подходит для состояния усталости")
        elif book_vector['complexity'] >= 4 and session.energy_level == 'high':
            reasons.append("Сложная книга подходит для состояния бодрости")


        user_tags = {tag.name for tag in session.selected_mood_tags.all()}
        book_tag_names = book_vector.get('mood_tag_names', [])

        matching_tags = user_tags & set(book_tag_names)
        if matching_tags:
            reasons.append(f"Соответствует выбранным настроениям: {', '.join(matching_tags)}")


        if book_vector['average_rating'] >= 4:
            reasons.append(f"Высокий рейтинг ({book_vector['average_rating']}/5)")

        return reasons

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики по книгам"""
        if self.books_df.empty:
            return {}

        stats = {
            'total_books': len(self.books_df),
            'avg_pace': self.books_df['pace'].mean(),
            'avg_complexity': self.books_df['complexity'].mean(),
            'pace_distribution': self.books_df['pace'].value_counts().to_dict(),
            'complexity_distribution': self.books_df['complexity'].value_counts().to_dict(),
        }

        return stats