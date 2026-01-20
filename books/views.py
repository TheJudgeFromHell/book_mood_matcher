# books/views.py
from django.shortcuts import render
from django.db.models import Q
from .models import Book

def home(request):
    books = Book.objects.all()[:6]
    total_books = Book.objects.count()
    return render(request, 'books/home.html', {
        'books': books,
        'total_books': total_books,
        'title': 'BookMood - Главная'
    })

def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {
        'books': books,
        'title': 'Все книги'
    })

def all_books(request):
    return book_list(request)

def selection(request):
    """Подбор книг по настроению и сложности"""
    # Получаем параметры
    mood = request.GET.get('mood', '')
    complexity = request.GET.get('complexity', '')

    recommended_books = []
    show_results = False

    if mood or complexity:
        show_results = True

        try:
            books = Book.objects.all()

            if mood:
                books = books.filter(mood=mood)
                print(f"🔍 Ищем книги с настроением: '{mood}'")
                print(f"📚 Найдено: {books.count()}")
                
            if complexity:
                books = books.filter(complexity=complexity)

            recommended_books = books[:6]

        except Exception as e:
            print(f"❌ Ошибка подбора: {e}")
            recommended_books = []

    # Словарь для формы: английский ключ → русское название с эмодзи
    MOOD_FORM_CHOICES = {
        'happy': ('Веселое', '😊'),
        'sad': ('Грустное', '😔'),
        'inspiring': ('Вдохновляющее', '✨'),
        'calm': ('Спокойное', '😌'),
        'adventurous': ('Приключенческое', '🏞️'),
        'romantic': ('Романтическое', '❤️'),
        'mysterious': ('Таинственное', '🕵️'),
        'thoughtful': ('Задумчивое', '🤔'),
    }

    # Словарь для отображения в результатах
    mood_display_dict = {key: f"{emoji} {label}" for key, (label, emoji) in MOOD_FORM_CHOICES.items()}

    context = {
        'title': 'Подобрать книгу',
        'mood': mood,
        'complexity': complexity,
        'recommended_books': recommended_books,
        'show_results': show_results,
        'mood_choices': MOOD_FORM_CHOICES,
        'mood_display_dict': mood_display_dict,
    }

    return render(request, 'books/selection.html', context)


# Поиск книг
def search_books(request):
    """Простой и надёжный поиск"""
    # Получаем запрос
    query = request.GET.get('q', '').strip()

    print(f"🎯 ЗАПРОС ПОИСКА: '{query}'")

    results = []
    if query:
        from django.db.models import Q

        # Ищем БЕЗ УЧЁТА РЕГИСТРА (icontains)
        results = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query)
        )

        print(f"📚 НАЙДЕНО РЕЗУЛЬТАТОВ: {len(results)}")

        # Для отладки покажем что нашли
        for book in results[:3]:  # Покажем первые 3
            print(f"   📖 {book.title} (автор: {book.author})")

    return render(request, 'books/search.html', {
        'results': results,
        'query': query,
        'title': f'Поиск: {query}' if query else 'Поиск книг'
    })


# Статистика
def statistics(request):
    """Страница со статистикой"""
    from django.db.models import Count

    # Статистика по настроениям
    mood_stats = Book.objects.values('mood').annotate(
        count=Count('id')
    ).order_by('-count')

    # Преобразуем английские ключи в русские названия
    MOOD_RU_NAMES = {
        'happy': 'Веселое',
        'sad': 'Грустное',
        'inspiring': 'Вдохновляющее',
        'calm': 'Спокойное',
        'adventurous': 'Приключенческое',
        'romantic': 'Романтическое',
        'mysterious': 'Таинственное',
        'thoughtful': 'Задумчивое',
    }

    for stat in mood_stats:
        stat['mood_ru'] = MOOD_RU_NAMES.get(stat['mood'], stat['mood'])

    # Статистика по сложности
    complexity_stats = Book.objects.values('complexity').annotate(
        count=Count('id')
    ).order_by('-count')

    # Популярные авторы
    top_authors = Book.objects.values('author').annotate(
        book_count=Count('id')
    ).order_by('-book_count')[:5]

    context = {
        'title': 'Статистика',
        'mood_stats': mood_stats,
        'complexity_stats': complexity_stats,
        'top_authors': top_authors,
        'total_books': Book.objects.count(),
    }

    return render(request, 'books/statistics.html', context)


# Детальная информация о книге
def book_detail(request, book_id):
    """Детальная информация о книге"""
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        book = None

    return render(request, 'books/book_detail.html', {
        'book': book,
        'title': book.title if book else 'Книга не найдена'
    })
