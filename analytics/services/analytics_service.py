import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
from django.utils import timezone
from books.models import ReadingSession, BookRecommendation, Book
from users.models import ReadingProfile


class AnalyticsService:

    @staticmethod
    def get_session_analytics(days: int = 30) -> Dict[str, Any]:
        date_from = timezone.now() - timedelta(days=days)

        sessions = ReadingSession.objects.filter(created_at__gte=date_from)

        if not sessions.exists():
            return {}

        data = []
        for session in sessions:
            data.append({
                'date': session.created_at.date(),
                'energy_level': session.energy_level,
                'time_available': session.time_available,
                'is_authenticated': session.user is not None,
            })

        df = pd.DataFrame(data)

        stats = {
            'total_sessions': len(df),
            'auth_sessions': df['is_authenticated'].sum(),
            'guest_sessions': len(df) - df['is_authenticated'].sum(),
            'most_common_energy': df['energy_level'].mode().iloc[0] if not df['energy_level'].mode().empty else None,
            'most_common_time': df['time_available'].mode().iloc[0] if not df['time_available'].mode().empty else None,
        }

        return stats

    @staticmethod
    def get_recommendation_analytics(days: int = 30) -> Dict[str, Any]:
        date_from = timezone.now() - timedelta(days=days)

        recommendations = BookRecommendation.objects.filter(
            session__created_at__gte=date_from,
            is_shown=True
        )

        if not recommendations.exists():
            return {}

        data = []
        for rec in recommendations:
            data.append({
                'book_title': rec.book.title,
                'relevance_score': rec.relevance_score,
                'is_clicked': rec.is_clicked,
                'session_id': rec.session.id,
            })

        df = pd.DataFrame(data)

        stats = {
            'total_recommendations': len(df),
            'click_rate': df['is_clicked'].mean() if len(df) > 0 else 0,
            'avg_relevance_score': df['relevance_score'].mean(),
            'top_books': df['book_title'].value_counts().head(10).to_dict(),
        }

        return stats

    @staticmethod
    def create_sessions_chart(days: int = 30) -> str:
        date_from = timezone.now() - timedelta(days=days)

        sessions = ReadingSession.objects.filter(created_at__gte=date_from)

        if not sessions.exists():
            return ""

        dates = [s.created_at.date() for s in sessions]
        date_counts = pd.Series(dates).value_counts().sort_index()

        plt.figure(figsize=(10, 6))
        date_counts.plot(kind='bar', color='skyblue', edgecolor='black')

        plt.title(f'Количество сессий по дням (последние {days} дней)')
        plt.xlabel('Дата')
        plt.ylabel('Количество сессий')
        plt.xticks(rotation=45)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return image_base64

    @staticmethod
    def create_energy_level_chart(days: int = 30) -> str:
        date_from = timezone.now() - timedelta(days=days)

        sessions = ReadingSession.objects.filter(created_at__gte=date_from)

        if not sessions.exists():
            return ""

        energy_levels = [s.energy_level for s in sessions]
        energy_counts = pd.Series(energy_levels).value_counts()

        energy_labels = {
            'low': 'Низкий',
            'medium': 'Средний',
            'high': 'Высокий'
        }

        labels = [energy_labels.get(level, level) for level in energy_counts.index]

        plt.figure(figsize=(8, 8))
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        plt.pie(energy_counts.values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title(f'Распределение уровней энергии пользователей\n(последние {days} дней)')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return image_base64

    @staticmethod
    def create_book_parameters_chart() -> str:
        books = Book.objects.filter(is_active=True)

        if not books.exists():
            return ""

        data = []
        for book in books:
            data.append({
                'pace': book.pace,
                'complexity': book.complexity,
                'emotional_intensity': book.emotional_intensity,
                'title': book.title[:20] + '...' if len(book.title) > 20 else book.title,
            })

        df = pd.DataFrame(data)

        plt.figure(figsize=(12, 8))

        scatter = plt.scatter(
            df['pace'],
            df['complexity'],
            c=df['emotional_intensity'],
            s=df['emotional_intensity'] * 50,
            alpha=0.6,
            cmap='viridis'
        )

        plt.colorbar(scatter, label='Эмоциональная насыщенность')
        plt.title('Распределение книг по параметрам')
        plt.xlabel('Темп чтения (1-медленный, 5-быстрый)')
        plt.ylabel('Сложность (1-простая, 5-сложная)')
        plt.grid(True, alpha=0.3)

        for i, row in df.sample(min(5, len(df))).iterrows():
            plt.annotate(row['title'], (row['pace'], row['complexity']),
                         fontsize=8, alpha=0.7)

        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return image_base64