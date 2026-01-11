from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from books.models import MoodTag


class ReadingProfile(models.Model):
    """Профиль читательских предпочтений пользователя"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='reading_profile',
        verbose_name='Пользователь'
    )


    profile_name = models.CharField(max_length=100, default='Основной', verbose_name='Название профиля')


    preferred_reading_time = models.IntegerField(
        default=30,
        verbose_name='Предпочитаемое время чтения (мин)',
        help_text='Сколько минут обычно уходит на одну сессию чтения'
    )
    preferred_complexity = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Предпочитаемая сложность'
    )


    favorite_mood_tags = models.ManyToManyField(
        MoodTag,
        blank=True,
        related_name='favored_by_profiles',
        verbose_name='Любимые теги настроений'
    )


    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Читательский профиль'
        verbose_name_plural = 'Читательские профили'

    def __str__(self):
        return f"Профиль {self.profile_name} - {self.user.username}"

    def get_preferred_complexity_display(self):
        complexity_texts = {
            1: 'Очень простые',
            2: 'Простые',
            3: 'Средние',
            4: 'Сложные',
            5: 'Очень сложные'
        }
        return complexity_texts.get(self.preferred_complexity, 'Не определено')


class ReadingSession(models.Model):
    """Модель для запроса подбора книги"""
    ENERGY_LEVELS = [
        ('low', 'Низкий (устал)'),
        ('medium', 'Средний'),
        ('high', 'Высокий (полон сил)'),
    ]

    TIME_AVAILABLE = [
        (15, '15 минут'),
        (30, '30 минут'),
        (60, '1 час'),
        (90, '1.5 часа'),
        (120, '2+ часа'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reading_sessions',
        verbose_name='Пользователь',
        null=True,
        blank=True
    )


    energy_level = models.CharField(
        max_length=20,
        choices=ENERGY_LEVELS,
        verbose_name='Уровень энергии'
    )
    current_mood = models.CharField(max_length=200, verbose_name='Текущее настроение', blank=True)


    time_available = models.IntegerField(
        choices=TIME_AVAILABLE,
        verbose_name='Доступное время'
    )
    desired_mood_after = models.CharField(
        max_length=200,
        verbose_name='Желаемое состояние после чтения',
        help_text='Какое настроение хочется получить после чтения?'
    )


    selected_mood_tags = models.ManyToManyField(
        MoodTag,
        blank=True,
        verbose_name='Выбранные теги настроений'
    )


    recommended_books = models.ManyToManyField(
        'books.Book',
        through='BookRecommendation',
        related_name='recommended_in_sessions',
        verbose_name='Рекомендованные книги'
    )


    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP адрес')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')

    class Meta:
        verbose_name = 'Сессия чтения'
        verbose_name_plural = 'Сессии чтения'
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else 'Гость'
        return f"Сессия {username} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"


class BookRecommendation(models.Model):
    """Промежуточная модель для связи книги и сессии с дополнительными данными"""
    session = models.ForeignKey(ReadingSession, on_delete=models.CASCADE, verbose_name='Сессия')
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE, verbose_name='Книга')

    relevance_score = models.FloatField(
        verbose_name='Оценка релевантности',
        help_text='Насколько книга подходит под запрос (0-1)'
    )

    match_reasons = models.JSONField(
        default=list,
        verbose_name='Причины рекомендации',
        help_text='Список причин, почему книга была рекомендована'
    )

    is_shown = models.BooleanField(default=False, verbose_name='Показана пользователю')
    is_clicked = models.BooleanField(default=False, verbose_name='Нажата пользователем')
    clicked_at = models.DateTimeField(null=True, blank=True, verbose_name='Время нажатия')

    class Meta:
        verbose_name = 'Рекомендация книги'
        verbose_name_plural = 'Рекомендации книг'
        unique_together = ['session', 'book']

    def __str__(self):
        return f"Рекомендация: {self.book.title} для сессии {self.session.id}"