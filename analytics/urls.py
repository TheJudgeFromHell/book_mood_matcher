from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Главная аналитика
    path('', views.analytics_dashboard, name='dashboard'),

    # Статистика по книгам
    path('books/', views.book_analytics, name='book_analytics'),

    # Статистика по пользователям
    path('users/', views.user_analytics, name='user_analytics'),

    # Популярные книги
    path('popular/', views.popular_books, name='popular_books'),

    # Отчеты
    path('reports/', views.reports, name='reports'),
]