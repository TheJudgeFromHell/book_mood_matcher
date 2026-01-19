from django.db import models
from django.contrib.auth.models import User


# МОДЕЛЬ 1: Book (уже есть)
class Book(models.Model):
    MOOD_CHOICES = [
        ('happy', 'Веселое'),
        ('sad', 'Грустное'),
        ('inspiring', 'Вдохновляющее'),
        ('calm', 'Спокойное'),
        ('adventurous', 'Приключенческое'),
        ('romantic', 'Романтическое'),
        ('mysterious', 'Таинственное'),
        ('thoughtful', 'Задумчивое'),
    ]

    COMPLEXITY_CHOICES = [
        ('easy', 'Легкая'),
        ('medium', 'Средняя'),
        ('hard', 'Сложная'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    author = models.CharField(max_length=100, verbose_name='Автор')
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES, verbose_name='Настроение')
    complexity = models.CharField(max_length=50, choices=COMPLEXITY_CHOICES, verbose_name='Сложность')
    description = models.TextField(verbose_name='Описание', blank=True)

    def __str__(self):
        return f"{self.title} - {self.author}"

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'


# МОДЕЛЬ 2: UserProfile (НОВАЯ)
class UserProfile(models.Model):
    READING_SPEED_CHOICES = [
        ('slow', 'Медленно'),
        ('medium', 'Средне'),
        ('fast', 'Быстро'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    favorite_genres = models.CharField(max_length=200, blank=True, verbose_name='Любимые жанры')
    reading_speed = models.CharField(
        max_length=20,
        choices=READING_SPEED_CHOICES,
        default='medium',
        verbose_name='Скорость чтения'
    )
    favorite_books = models.ManyToManyField(Book, blank=True, verbose_name='Избранные книги')

    def __str__(self):
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


# МОДЕЛЬ 3: BookSelection (НОВАЯ)
class BookSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    selected_mood = models.CharField(max_length=50, choices=Book.MOOD_CHOICES, verbose_name='Выбранное настроение')
    selected_complexity = models.CharField(max_length=50, choices=Book.COMPLEXITY_CHOICES,
                                           verbose_name='Выбранная сложность')
    selected_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата подбора')
    recommended_books = models.ManyToManyField(Book, verbose_name='Рекомендованные книги')

    def __str__(self):
        return f"Подборка {self.user.username} от {self.selected_date.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = 'Подборка книг'
        verbose_name_plural = 'Подборки книг'
        ordering = ['-selected_date']  # Сначала новые


# Сигналы для автоматического создания профиля при создании пользователя
# ЭТО ДОЛЖНО БЫТЬ ВНЕ ВСЕХ КЛАССОВ!
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создать профиль при создании нового пользователя"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохранить профиль при сохранении пользователя"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()