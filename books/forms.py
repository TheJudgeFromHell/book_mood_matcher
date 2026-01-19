from django import forms
from .models import Book


class BookSelectionForm(forms.Form):
    """Форма для подбора книг по настроению"""

    mood = forms.ChoiceField(
        choices=Book.MOOD_CHOICES,
        label='🎭 Ваше текущее настроение',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'font-size: 16px; padding: 10px;'
        })
    )

    complexity = forms.ChoiceField(
        choices=Book.COMPLEXITY_CHOICES,
        label='📊 Уровень сложности',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'font-size: 16px; padding: 10px;'
        })
    )

    time_available = forms.ChoiceField(
        choices=[
            ('short', '⏱️ Мало времени (15-30 минут)'),
            ('medium', '🕐 Средне (1-2 часа)'),
            ('long', '🕔 Много времени (более 2 часов)'),
        ],
        label='⏰ Сколько времени готовы уделить чтению?',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'font-size: 16px; padding: 10px;'
        })
    )

    genre_preference = forms.ChoiceField(
        choices=[
            ('any', '🎭 Любой жанр'),
            ('classic', '📚 Классика'),
            ('fantasy', '🐉 Фэнтези'),
            ('novel', '💖 Роман'),
            ('detective', '🔍 Детектив'),
            ('biography', '👤 Биография'),
        ],
        label='📖 Предпочтительный жанр',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'font-size: 16px; padding: 10px;'
        })
    )


class SearchForm(forms.Form):
    """Форма для поиска книг"""
    query = forms.CharField(
        max_length=100,
        label='🔍 Поиск книг',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите название или автора...',
            'style': 'font-size: 16px; padding: 10px;'
        })
    )