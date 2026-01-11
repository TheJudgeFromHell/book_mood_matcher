from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from .services.analytics_service import AnalyticsService


@login_required
@permission_required('analytics.view_analytics', raise_exception=True)
def analytics_dashboard(request):
    session_stats = AnalyticsService.get_session_analytics(30)
    recommendation_stats = AnalyticsService.get_recommendation_analytics(30)

    sessions_chart = AnalyticsService.create_sessions_chart(30)
    energy_chart = AnalyticsService.create_energy_level_chart(30)
    book_params_chart = AnalyticsService.create_book_parameters_chart()

    context = {
        'title': 'Панель аналитики',
        'session_stats': session_stats,
        'recommendation_stats': recommendation_stats,
        'sessions_chart': sessions_chart,
        'energy_chart': energy_chart,
        'book_params_chart': book_params_chart,
    }

    return render(request, 'analytics/dashboard.html', context)


@login_required
def user_analytics(request):
    if not hasattr(request.user, 'reading_profile'):
        from users.models import ReadingProfile
        ReadingProfile.objects.create(user=request.user)

    profile = request.user.reading_profile

    user_sessions = request.user.reading_sessions.all().order_by('-created_at')[:10]

    saved_books = request.user.userbookinteraction_set.filter(
        interaction_type='save'
    ).select_related('book')[:10]


    liked_books = request.user.userbookinteraction_set.filter(
        interaction_type='like'
    ).select_related('book')[:10]

    context = {
        'title': 'Моя статистика',
        'profile': profile,
        'user_sessions': user_sessions,
        'saved_books': saved_books,
        'liked_books': liked_books,
    }

    return render(request, 'analytics/user_stats.html', context)