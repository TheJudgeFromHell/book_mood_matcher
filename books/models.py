from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    """Модель жанра книги"""
    name = models.CharField(max_length=100, verbose_name='Название жанра')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class MoodTag(models.Model):
    """Модель тега настроения/состояния"""
    MOOD_TYPES = [
        ('energy', 'Энергия'),
        ('emotion', 'Эмоция'),
        ('situation', 'Ситуация'),
        ('goal', 'Цель'),
    ]

    name = models.CharField(max_length=100, verbose_name='Название тега')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')
    mood_type = models.CharField(max_length=20, choices=MOOD_TYPES, default='emotion', verbose_name='Тип настроения')
    description = models.TextField(blank=True, verbose_name='Описание')
    emoji = models.CharField(max_length=5, blank=True, verbose_name='Эмодзи')

    class Meta:
        verbose_name = 'Тег настроения'
        verbose_name_plural = 'Теги настроений'
        ordering = ['mood_type', 'name']

    def __str__(self):
        return f"{self.emoji} {self.name}"


class Book(models.Model):
    """Основная модель книги"""
    title = models.CharField(max_length=300, verbose_name='Название книги')
    author = models.CharField(max_length=200, verbose_name='Автор')
    isbn = models.CharField(max_length=20, blank=True, verbose_name='ISBN', unique=True)
    description = models.TextField(verbose_name='Описание')
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, related_name='books', verbose_name='Жанр')


    pace = models.IntegerField(
        verbose_name='Темп чтения',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='1 - очень медленный/сложный, 5 - очень быстрый/легкий'
    )
    complexity = models.IntegerField(
        verbose_name='Сложность',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='1 - очень простая, 5 - очень сложная'
    )
    emotional_intensity = models.IntegerField(
        verbose_name='Эмоциональная насыщенность',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
        help_text='1 - спокойная, 5 - очень эмоциональная'
    )

    mood_tags = models.ManyToManyField(MoodTag, related_name='books', verbose_name='Теги настроения')

    page_count = models.PositiveIntegerField(verbose_name='Количество страниц', null=True, blank=True)
    # ВРЕМЕННО: закомментировали ImageField
    # cover_image = models.ImageField(upload_to='book_covers/', verbose_name='Обложка', null=True, blank=True)
    cover_url = models.URLField(verbose_name='Ссылка на обложку', blank=True)

    google_books_id = models.CharField(max_length=50, blank=True, verbose_name='ID Google Books')
    published_date = models.CharField(max_length=20, blank=True, verbose_name='Дата публикации')
    publisher = models.CharField(max_length=200, blank=True, verbose_name='Издательство')
    language = models.CharField(max_length=10, default='ru', verbose_name='Язык')

    average_rating = models.FloatField(default=0, verbose_name='Средний рейтинг')
    ratings_count = models.IntegerField(default=0, verbose_name='Количество оценок')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']
        indexes = [
            models.Index(fields=['pace', 'complexity']),
            models.Index(fields=['title']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f"{self.title} - {self.author}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('book_detail', args=[str(self.pk)])

    def get_pace_display_text(self):
        pace_texts = {
            1: 'Очень медленный',
            2: 'Медленный',
            3: 'Средний',
            4: 'Быстрый',
            5: 'Очень быстрый'
        }
        return pace_texts.get(self.pace, 'Не определено')

    def get_complexity_display_text(self):
        complexity_texts = {
            1: 'Очень простая',
            2: 'Простая',
            3: 'Средняя',
            4: 'Сложная',
            5: 'Очень сложная'
        }
        return complexity_texts.get(self.complexity, 'Не определено')


class UserBookInteraction(models.Model):
    """Взаимодействия пользователя с книгами"""
    INTERACTION_TYPES = [
        ('view', 'Просмотр'),
        ('save', 'Сохранение'),
        ('read', 'Прочитано'),
        ('like', 'Понравилось'),
        ('dislike', 'Не понравилось'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES, verbose_name='Тип взаимодействия')

    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    review = models.TextField(blank=True, verbose_name='Отзыв')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата взаимодействия')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Взаимодействие пользователя'
        verbose_name_plural = 'Взаимодействия пользователей'
        unique_together = ['user', 'book', 'interaction_type']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_interaction_type_display()} - {self.book.title}"
