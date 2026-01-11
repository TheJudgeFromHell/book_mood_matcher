from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .forms import BookImportForm, BookRecommendationForm
from .services.recommendation_engine import RecommendationEngine
from .models import Book, ReadingSession, BookRecommendation, UserBookInteraction

@login_required
@permission_required('books.add_book', raise_exception=True)
def import_book_view(request):
    """Представление для импорта книг"""
    if request.method == 'POST':
        form = BookImportForm(request.POST)
        if form.is_valid():
            result = form.import_book()

            if result['success']:
                messages.success(request, result['message'])
                if 'book' in result:
                    return redirect('book_detail', book_id=result['book'].id)
                return redirect('book_list')
            else:
                messages.error(request, result['message'])
    else:
        form = BookImportForm()

    return render(request, 'books/import_book.html', {
        'form': form,
        'title': 'Импорт книги по ISBN'
    })

def book_recommendation_view(request):
    """Основное представление для рекомендации книг"""
    recommendation_engine = RecommendationEngine()

    if request.method == 'POST':
        form = BookRecommendationForm(request.POST)
        if form.is_valid():
            # Создаем сессию чтения
            session = ReadingSession.objects.create(
                user=request.user if request.user.is_authenticated else None,
                energy_level=form.cleaned_data['energy_level'],
                current_mood=form.cleaned_data['current_mood'],
                time_available=form.cleaned_data['time_available'],
                desired_mood_after=form.cleaned_data['desired_mood_after'],
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )


            if form.cleaned_data['mood_tags']:
                session.selected_mood_tags.set(form.cleaned_data['mood_tags'])


            recommendations = recommendation_engine.recommend_books(session)


            recommended_books = []
            for rec in recommendations:
                book = Book.objects.get(id=rec['book_id'])
                BookRecommendation.objects.create(
                    session=session,
                    book=book,
                    relevance_score=rec['relevance_score'],
                    match_reasons=rec['match_reasons'],
                    is_shown=True
                )
                recommended_books.append(book)


            session.save()

            return render(request, 'books/recommendation_results.html', {
                'session': session,
                'recommended_books': recommended_books[:5],
                'form': form,
            })
    else:
        form = BookRecommendationForm()


    stats = recommendation_engine.get_statistics()

    return render(request, 'books/recommendation_form.html', {
        'form': form,
        'stats': stats,
        'title': 'Подбор книги по настроению'
    })


@require_POST
def save_recommendation_feedback(request):
    """Сохранение обратной связи по рекомендации"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Требуется авторизация'})

    recommendation_id = request.POST.get('recommendation_id')
    feedback_type = request.POST.get('feedback_type')  # 'like', 'dislike', 'save'

    try:
        recommendation = BookRecommendation.objects.get(
            id=recommendation_id,
            session__user=request.user
        )

        if feedback_type == 'like':
            recommendation.is_clicked = True
            recommendation.clicked_at = timezone.now()
            recommendation.save()


            UserBookInteraction.objects.create(
                user=request.user,
                book=recommendation.book,
                interaction_type='like'
            )

        elif feedback_type == 'save':
            UserBookInteraction.objects.create(
                user=request.user,
                book=recommendation.book,
                interaction_type='save'
            )

        return JsonResponse({'success': True})

    except BookRecommendation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Рекомендация не найдена'})